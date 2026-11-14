"""Assemble separately authored accessories around the cleaned StableGen body.
Run with Blender --python-exit-code 2 --python script.py -- --body file.blend --output folder.
"""
import bpy, math, json, argparse, sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--body',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(a.body.resolve()));body=next(o for o in bpy.context.scene.objects if o.type=='MESH');body.name='Cuerpo_StableGen';parts=[body]
for o in list(bpy.context.scene.objects):
 if o!=body:bpy.data.objects.remove(o,do_unlink=True)
scene=bpy.context.scene

def mat(name,color,rough=.7,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
orange=mat('Pelaje_naranja',(.7,.22,.045));cream=mat('Pelaje_crema',(.91,.85,.68));pink=mat('Nariz_pies_orejas',(.65,.23,.20));black=mat('Ojos_negros',(.006,.004,.003),.12);olive=mat('Tela_oliva',(.18,.23,.035));leather=mat('Cuero_marron',(.22,.075,.026));gold=mat('Herrajes',(.55,.32,.075),.35,.65);green=mat('Brote_verde',(.38,.50,.035))
body.data.materials.clear()
for m in [orange,cream,pink]:body.data.materials.append(m)
bpy.context.view_layer.objects.active=body;body.select_set(True);body.data.calc_loop_triangles();before=len(body.data.loop_triangles)
mo=body.modifiers.new('Exploratory_reduction_14000','DECIMATE');mo.ratio=min(1,14000/max(before,1));mo.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mo.name)
# Smooth authored vertex colors; the reference is not used as an image texture.
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
body.data.materials.clear();body.data.materials.append(orange)
col=body.data.color_attributes.new(name='CoatColor',type='FLOAT_COLOR',domain='CORNER')
for polygon in body.data.polygons:
 polygon.material_index=0;polygon.use_smooth=True
 for li in polygon.loop_indices:
  x,y,z=body.data.vertices[body.data.loops[li].vertex_index].co
  band=(1-smooth(.023,.044,abs(x)))*(1-smooth(-.205,-.17,y))
  muzzle=(1-smooth(-.067,-.043,z))*(1-smooth(-.205,-.17,y))
  belly=1-smooth(-.115,-.088,z)
  w=max(band,muzzle,belly);foot=1-smooth(-.15,-.135,z)
  c=[(.7,.22,.045)[i]*(1-w)+(.91,.85,.68)[i]*w for i in range(3)]
  c=[c[i]*(1-foot)+(.65,.23,.20)[i]*foot for i in range(3)]
  col.data[li].color=(*c,1)
vc=orange.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='CoatColor';orange.node_tree.links.new(vc.outputs['Color'],orange.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
root=bpy.data.objects.new('Cuy_Modular',None);scene.collection.objects.link(root);body.parent=root

def add(o,name,m,parent=root):
 o.name=name;o.data.materials.append(m);o.parent=parent;o['provenance']='Separately authored Blender accessory; not StableGen-generated';parts.append(o);return o

def ell(name,pos,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=pos);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for f in o.data.polygons:f.use_smooth=True
 return add(o,name,m)

def box(name,pos,scale,m,bevel=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mo=o.modifiers.new('Rounded_edges','BEVEL');mo.width=bevel;mo.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mo.name)
 for f in o.data.polygons:f.use_smooth=True
 return add(o,name,m)

def tube(name,points,radius,m):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=2;c.bevel_depth=radius;c.bevel_resolution=1;s=c.splines.new('POLY');s.points.add(len(points)-1)
 for v,q in zip(s.points,points):v.co=(*q,1)
 o=bpy.data.objects.new(name,c);scene.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');return add(bpy.context.object,name,m)
pack=box('Mochila_cuerpo',(0,.145,.006),(.205,.095,.185),olive,.018)
flap=box('Mochila_solapa',(0,.199,.062),(.215,.035,.08),leather,.016)
for s in [-1,1]:
 box('Bolsillo_'+str(s),(s*.107,.154,-.012),(.05,.075,.095),olive,.012)
 box('Bolsillo_solapa_'+str(s),(s*.112,.194,.02),(.052,.016,.038),leather,.007)
 # Fitted side straps are distinct editable objects; fit remains subject to pose checks.
 pts=[(s*.099,.132,.096),(s*.138,.068,.077),(s*.154,-.035,.035),(s*.153,-.03,-.07),(s*.123,.075,-.091),(s*.087,.14,-.07)]
 # Project intermediate samples onto the actual torso, preserving backpack attachment endpoints.
 fitted=[pts[0]]
 origin=Vector((0,-.045,-.035))
 for index in range(len(pts)-1):
  for j in range(1,7):
   q=Vector(pts[index]).lerp(Vector(pts[index+1]),j/6)
   if index==len(pts)-2 and j==6:continue
   direction=(q-origin).normalized();hit,point,normal,_=body.ray_cast(origin+direction, -direction)
   fitted.append(tuple(point+normal*.004) if hit else tuple(q))
 fitted.append(pts[-1]);tube('Correa_'+str(s),fitted,.005,leather)
box('Cierre_frontal',(0,.219,.007),(.026,.012,.095),leather,.005)
# Rectangular buckle perimeter remains separate from strap.
tube('Hebilla',[( -.019,.229,.028),(.019,.229,.028),(.019,.229,-.003),(-.019,.229,-.003),(-.019,.229,.028)],.003,gold)
tube('Asa', [(-.033,.15,.10),(-.03,.15,.14),(.03,.15,.14),(.033,.15,.10)],.006,leather)
for s in [-1,1]:
 ell('Ojo_'+str(s),(s*.078,-.253,.012),(.025,.016,.029),black)
ell('Nariz',(0,-.296,-.019),(.012,.007,.008),pink)
# A separate leaf mesh, stem and leaf ornaments, with useful pivots at their attachments.
tube('Brote_tallo',[(0,-.13,.095),(0,-.13,.13),(.012,-.128,.16)],.003,green)
def leaf(name,base,tip,width):
 b=Vector(base);t=Vector(tip);d=t-b;side=d.cross(Vector((0,1,0))).normalized()*width;vs=[b,b+d*.35+side,b+d*.72+side*.65,t,b+d*.72-side*.65,b+d*.35-side,b+d*.5+Vector((0,-.004,0))];faces=[(6,i,(i+1)%6) for i in range(6)];mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);add(o,name,green);mo=o.modifiers.new('Leaf_thickness','SOLIDIFY');mo.thickness=.001;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mo.name)
leaf('Brote_hoja',(.008,-.128,.145),(.062,-.122,.205),.025)
leaf('Adorno_mochila_hoja',(-.06,.222,-.027),(-.03,.222,.017),.013)
# Export independently editable modules as well as the complete assembly.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.export_scene.gltf(filepath=str(out/'cuy-stablegen-modular.glb'),export_format='GLB',use_selection=True,export_animations=False)
for name,objs in [('cuerpo',[body]+[o for o in parts if o.name.startswith(('Ojo','Nariz'))]),('mochila',[o for o in parts if o not in [body] and not o.name.startswith(('Brote','Ojo','Nariz'))]),('brote',[o for o in parts if o.name.startswith('Brote')])]:
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',use_selection=True,export_animations=False)
scene.world=bpy.data.worlds.new('Studio');scene.world.color=(.1,.1,.1);scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.max_bounces=3;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=700;scene.render.resolution_y=700;scene.render.resolution_percentage=100
center=Vector((0,-.045,.005))
for loc,power in [((-1,-2,2),30),((1,-1,.6),12),((0,2,1),20)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(loc)*.4);o=bpy.context.object;o.data.energy=power;o.data.size=.8;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.57
for name,d in [('frente',(0,-1,.15)),('tres-cuartos',(1,-1,.55)),('espalda',(1,1,.45))]:
 cam.location=center+Vector(d).normalized();cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/('final-'+name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'cuy-stablegen-modular.blend'))
rows=[]
for o in parts:o.data.calc_loop_triangles();rows.append({'name':o.name,'triangles':len(o.data.loop_triangles),'provenance':o.get('provenance','StableGen geometry with local manual reconstruction')})
(out/'assembly-manifest.json').write_text(json.dumps({'body_source':a.body.name,'parts':rows,'triangles':sum(r['triangles'] for r in rows),'rig':False,'animations':False,'texture_generation':False,'limits':'Exploratory modular model; color and accessories manually authored. No mobile performance, rig, facial or animation certification.'},indent=2))
print('MODULAR_ASSEMBLY_COMPLETE',sum(r['triangles'] for r in rows))
