"""Small, sequential, reproducible fur-card experiment. No game repository writes."""
import bpy, sys, math, time, random, json, bisect
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'artifacts'

MODE='library'
random.seed(371)
scene=None

def setup():
    global scene
    scene=bpy.context.scene
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='CUDA'; prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='CUDA'
    scene.cycles.device='GPU';scene.cycles.samples=32
    scene.cycles.use_denoising=True; scene.cycles.max_bounces=4
    scene.cycles.transparent_max_bounces=12
    scene.render.simplify_subdivision=1
    scene.render.simplify_subdivision_render=1
    scene.render.use_persistent_data=False
    scene.render.threads_mode='FIXED';scene.render.threads=4
    scene.render.resolution_x=768;scene.render.resolution_y=768
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.world.color=(.24,.24,.24)
    scene.view_settings.view_transform='AgX'

def coat(p):
    # Smooth world-space boundary; shading and cards share exactly the same colors.
    boundary=.13+.065*math.sin(p.x*7)+.045*math.sin(p.z*14+p.x*4)
    t=max(0,min(1,(p.y-boundary+.055)/.11)); t=t*t*(3-2*t)
    light=Vector((.68,.53,.34)); dark=Vector((.27,.095,.027))
    return tuple(light.lerp(dark,t))

def set_colors(o):
    mesh=o.data
    attr=mesh.color_attributes.get('COAT') or mesh.color_attributes.new(name='COAT',type='FLOAT_COLOR',domain='CORNER')
    for loop in mesh.loops:
        color=coat(o.matrix_world@mesh.vertices[loop.vertex_index].co)
        attr.data[loop.index].color=(*color,1)
    mesh.color_attributes.active_color=attr

def normal_texture():
    w=h=256
    y,x=np.mgrid[0:h,0:w].astype(float);x/=w;y/=h
    # Tileable fine directional fiber relief, encoded as a tangent-space normal map.
    a=2*math.pi
    dx=.14*np.sin(a*(x*39+np.sin(a*y)*.32))+.08*np.sin(a*(x*61+y*3))
    dy=.035*np.sin(a*(y*11+x*7))
    z=np.ones_like(dx);norm=np.sqrt(dx*dx+dy*dy+z*z)
    pixels=np.stack((dx/norm*.5+.5,dy/norm*.5+.5,z/norm*.5+.5,np.ones_like(z)),axis=-1).astype(np.float32)
    image=bpy.data.images.new('Pelaje_micro_normal_256',width=w,height=h,alpha=True)
    image.colorspace_settings.name='Non-Color';image.pixels.foreach_set(pixels.ravel())
    image.filepath_raw=str(OUT/'pelaje-normal-256.png');image.file_format='PNG';image.save();image.pack()
    return image

def base_material(image):
    m=bpy.data.materials.new('Pelaje_base_normal_y_color_vertices')
    n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
    col=n.new('ShaderNodeVertexColor');col.layer_name='COAT';l.new(col.outputs['Color'],bs.inputs['Base Color'])
    uv=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(9,5,1)
    tex=n.new('ShaderNodeTexImage');tex.image=image
    normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.50
    l.new(uv.outputs['UV'],mapping.inputs['Vector']);l.new(mapping.outputs['Vector'],tex.inputs['Vector'])
    l.new(tex.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs['Normal'],bs.inputs['Normal'])
    bs.inputs['Roughness'].default_value=.76
    return m

def stats(objects):
    out={'mesh_objects':len(objects),'vertices':0,'triangles':0}
    for o in objects:
        o.data.calc_loop_triangles();out['vertices']+=len(o.data.vertices);out['triangles']+=len(o.data.loop_triangles)
    return out

def render(name):
    scene.render.filepath=str(OUT/(name+'.png'));t=time.perf_counter()
    bpy.ops.render.render(write_still=True)
    return round(time.perf_counter()-t,3)

def alpha_atlas():
    w,h=512,256
    arr=np.zeros((h,w,4),dtype=np.float32);arr[:,:,:3]=1
    yy,xx=np.mgrid[0:h,0:128].astype(float); yy/=h;xx/=128
    for tile in range(4):
        alpha=np.zeros_like(xx)
        for strand in range(9):
            center=.10+strand*.095+random.uniform(-.018,.018)
            end=random.uniform(.62,.98)
            curve=center+random.uniform(-.09,.09)*yy**2+.018*np.sin(yy*7+strand)
            width=.009*(1-yy*.70)
            a=np.exp(-((xx-curve)/width)**2*2)
            a*=np.clip((end-yy)*24,0,1)*np.clip(yy*45,0,1)
            alpha=np.maximum(alpha,a)
        arr[:,tile*128:(tile+1)*128,3]=alpha
    image=bpy.data.images.new('Atlas_mechones_512x256',width=w,height=h,alpha=True)
    image.pixels.foreach_set(arr.ravel());image.filepath_raw=str(OUT/'pelaje-mechones-512x256.png')
    image.file_format='PNG';image.save();image.pack()
    return image

def card_material(image):
    m=bpy.data.materials.new('Mechones_alpha_recortado')
    m.surface_render_method='DITHERED';m.use_backface_culling=False
    n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF')
    tex=n.new('ShaderNodeTexImage');tex.image=image
    col=n.new('ShaderNodeVertexColor');col.layer_name='COAT'
    l.new(col.outputs['Color'],bs.inputs['Base Color'])
    cut=n.new('ShaderNodeMath');cut.operation='GREATER_THAN';cut.inputs[1].default_value=.23
    l.new(tex.outputs['Alpha'],cut.inputs[0]);l.new(cut.outputs[0],bs.inputs['Alpha'])
    bs.inputs['Roughness'].default_value=.70
    return m

def surface_data(sources):
    data=[];cumulative=[];total=0
    for o in sources:
        mesh=o.data;mesh.calc_loop_triangles()
        pts=[o.matrix_world@v.co for v in mesh.vertices]
        norms=[(o.matrix_world.to_3x3()@v.normal).normalized() for v in mesh.vertices]
        bvh=BVHTree.FromPolygons(pts,[p.vertices[:] for p in mesh.polygons])
        triangles=[];weights=[];area=0
        for tri in mesh.loop_triangles:
            a,b,c=[pts[i] for i in tri.vertices];size=(b-a).cross(c-a).length/2
            area+=size;weights.append(area);triangles.append(tuple(tri.vertices))
        data.append({'object':o,'pts':pts,'norms':norms,'bvh':bvh,'triangles':triangles,'weights':weights,'area':area})
        total+=area;cumulative.append(total)
    return data,cumulative,total

def sample(data,cumulative,total):
    source=data[bisect.bisect_left(cumulative,random.random()*total)]
    tri=source['triangles'][bisect.bisect_left(source['weights'],random.random()*source['area'])]
    r=math.sqrt(random.random());s=random.random();weights=(1-r,r*(1-s),r*s)
    p=sum((source['pts'][i]*w for i,w in zip(tri,weights)),Vector())
    normal=sum((source['norms'][i]*w for i,w in zip(tri,weights)),Vector()).normalized()
    if p.z<.26:return None
    # Reject interior overlap areas. No fur on eyes, nose, lips or inner ears.
    for other in data:
        if other is source:continue
        q,n,idx,distance=other['bvh'].find_nearest(p)
        if q is not None and (p-q).dot(n)<-.006:return None
    if False:
        for side in (-1,1):
            eye=Vector((side*.422,-1.09,1.035))
            if (p-eye).length<.127:return None
    return p,normal,source['object'].name

def cards(count,data,cumulative,total,mat,name):
    verts=[];faces=[];uvs=[];colors=[];roots=[];normals=[]
    attempts=0
    while len(roots)<count and attempts<count*10:
        attempts+=1;s=sample(data,cumulative,total)
        if not s:continue
        p,n,part=s
        length=random.uniform(.045,.085)
        if part.startswith('03_'):length*=.45
        direction=Vector((p.x*.25,1,-.22))
        tangent=direction-n*direction.dot(n)
        if tangent.length<.01:tangent=n.orthogonal()
        tangent.normalize()
        cross=n.cross(tangent).normalized()
        # Broadly upright, bent backward; each ribbon carries nine fine hairs.
        width=random.uniform(.035,.052)
        tile=random.randrange(4);idx=len(verts)
        color=Vector(coat(p))*random.uniform(.90,1.10)
        for row,t in enumerate((0,.52,1)):
            center=p+n*(-.003+length*t*.83)+tangent*(length*t*t*.52)
            half=width*.5*(1-t*.12)
            for sign in (-1,1):
                verts.append(tuple(center+cross*half*sign))
                uvs.append(((tile+(sign+1)*.5)/4,t))
                colors.append((*color,1))
                normals.append(tuple(n))
        faces.extend([(idx,idx+1,idx+3,idx+2),(idx+2,idx+3,idx+5,idx+4)])
        roots.append(tuple(p))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.data.collections['CUY_personaje'].objects.link(obj)
    mesh.materials.append(mat);uv=mesh.uv_layers.new(name='UVMap')
    color=mesh.color_attributes.new(name='COAT',type='FLOAT_COLOR',domain='CORNER')
    for loop in mesh.loops:
        uv.data[loop.index].uv=uvs[loop.vertex_index];color.data[loop.index].color=colors[loop.vertex_index]
    mesh.color_attributes.active_color=color
    # Surface-like normals avoid a harsh card-shaped specular highlight.
    for face in mesh.polygons:face.use_smooth=True
    mesh.normals_split_custom_set_from_vertices(normals)
    obj['cards']=len(roots);obj['physics']='Static; guide simulation not implemented'
    return obj
