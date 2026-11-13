"""Procedural stylized guinea pig: staged model, groom, skin and baked spring demo."""
import bpy,sys,math,json,time,random,argparse,struct
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
import fur_tools as f
args=argparse.ArgumentParser();args.add_argument('--output',required=True);args.add_argument('--stage',choices=['model','groom','rig','preview'],required=True)
a=args.parse_args(sys.argv[sys.argv.index('--')+1:]);OUT=Path(a.output).resolve();OUT.mkdir(parents=True,exist_ok=True)
f.OUT=OUT;random.seed(802)
def mat(name,color,rough=.65):
    m=bpy.data.materials.new(name);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;return m
def coat(p):
    cream=Vector((.83,.70,.49));orange=Vector((.47,.18,.045))
    if p.y<-.35:
        width=.16+.05*max(0,1.2-p.z)
        t=max(0,min(1,(abs(p.x)-width)/.06))
        if p.z<.99 and p.y<-.96:t*=max(0,min(1,(p.z-.86)/.13))
    else:
        t=max(0,min(1,(p.y-.24+.07*math.sin(8*p.x)+.04*math.sin(14*p.z))/.12))
        if .45<p.y<.66:t*=.15
    t=t*t*(3-2*t);return tuple(cream.lerp(orange,t))
f.coat=coat
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def setup():
    bpy.context.scene.render.engine='CYCLES';f.setup();s=bpy.context.scene
    s.render.resolution_x=768;s.render.resolution_y=768;s.cycles.samples=40
    s.render.simplify_subdivision=0;s.render.simplify_subdivision_render=0
    return s
parts=[]
def sphere(name,pos,scale,m,seg=20,rings=12,bone='Body'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=pos)
    o=bpy.context.object;o.name=name
    for v in o.data.vertices:v.co.x*=scale[0];v.co.y*=scale[1];v.co.z*=scale[2]
    o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    for c in list(o.users_collection):c.objects.unlink(o)
    bpy.data.collections['CUY_personaje'].objects.link(o);o['bone']=bone;parts.append(o);return o
def tube(name,points,radius,m,bone):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=0
    sp=c.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for p,v in zip(sp.bezier_points,points):p.co=v;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    c.resolution_u=4;o=bpy.data.objects.new(name,c);bpy.data.collections['CUY_personaje'].objects.link(o);c.materials.append(m)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object;o['bone']=bone;parts.append(o);return o
def leaf(name,start,end,width,m,bone):
    st=Vector(start);en=Vector(end);direction=en-st;cross=direction.cross(Vector((0,-1,.3))).normalized()
    vs=[];faces=[]
    for i in range(7):
        t=i/6;center=st+direction*t+Vector((0,-.045*math.sin(t*math.pi),.035*math.sin(t*math.pi)))
        w=max(.001,width*math.sin(math.pi*t)**.7)
        vs.extend([tuple(center-cross*w),tuple(center+Vector((0,-.018,0))),tuple(center+cross*w)])
    for i in range(6):
        j=i*3;faces.extend([(j,j+3,j+4,j+1),(j+1,j+4,j+5,j+2)])
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.materials.append(m)
    o=bpy.data.objects.new(name,me);bpy.data.collections['CUY_personaje'].objects.link(o);o['bone']=bone;parts.append(o)
    tube(name+'_nervio',[start,tuple(st+direction*.5+Vector((0,-.06,.02))),end],.006,vein,bone)
    return o

if a.stage=='model':
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    col=bpy.data.collections.new('CUY_personaje');bpy.context.scene.collection.children.link(col)
    s=setup();base=f.base_material(f.normal_texture())
    pink=mat('Piel_orejas',(.52,.19,.11));paw=mat('Patitas',(.30,.14,.075));nail=mat('Unas',(.42,.28,.15));black=mat('Ojos',(.006,.003,.002),.12)
    nose=mat('Nariz',(.42,.12,.07),.45);lip=mat('Boca',(.09,.023,.014));tongue=mat('Lengua',(.50,.13,.10))
    leather=mat('Mochila_cuero',(.12,.065,.025));strap=mat('Correas',(.065,.045,.018));green=mat('Hojas',(.24,.34,.035));vein=mat('Nervios_hojas',(.39,.40,.08))
    sphere('01_Cuerpo',(0,.20,.77),(.70,.99,.64),base,32,20)
    sphere('02_Cabeza',(0,-.58,1.00),(.62,.63,.59),base,32,20,'Head')
    for side in (-1,1):
        sphere('03_Mejilla_'+str(side),(side*.17,-1.13,.94),(.27,.18,.22),base,20,12,'Head')
        ear=sphere('Oreja_'+str(side),(side*.54,-.44,1.43),(.19,.085,.20),base,16,12,'Head');ear.rotation_euler.y=side*.50
        ear=sphere('Oreja_interior_'+str(side),(side*.54,-.516,1.43),(.135,.035,.145),pink,16,10,'Head');ear.rotation_euler.y=side*.50
        sphere('Ojo_'+str(side),(side*.34,-1.095,1.18),(.143,.103,.166),black,24,16,'Head')
        for y,label in [(-.63,'Front'),(.68,'Back')]:
            name=label+('_L' if side<0 else '_R')
            sphere('Pata_'+name,(side*.46,y,.16),(.135,.20,.10),paw,16,10,'Foot_'+name)
            for j in (-1,0,1):sphere('Una_'+name+'_'+str(j),(side*.46+j*.052,y-.17,.135),(.022,.045,.023),nail,8,6,'Foot_'+name)
        for i in range(3):tube('Bigote',[ (side*.18,-1.32,.94-i*.035),(side*.43,-1.36,.96-i*.07),(side*.68,-1.27,1.01-i*.105)],.002,base,'Head')
        tube('Correa_'+str(side),[(side*.48,-.10,1.17),(side*.57,.18,1.26),(side*.37,.43,1.41)],.025,strap,'Body')
    # Soft triangular nose rather than a spherical button.
    sphere('Nariz',(0,-1.329,1.035),(.085,.039,.048),nose,12,8,'Head')
    mouth=sphere('Expresion_boca',(0,-1.304,.91),(.090,.027,.009),lip,20,12,'Head')
    mouth.shape_key_add(name='Basis');op=mouth.shape_key_add(name='OpenMouth');sm=mouth.shape_key_add(name='Smile')
    for v,p,q in zip(mouth.data.vertices,op.data,sm.data):p.co.z=v.co.z*8;q.co.z=v.co.z+.060*(abs(v.co.x)/.09)**1.8
    tongue_obj=sphere('Lengua',(0,-1.235,.878),(.045,.020,.012),tongue,12,8,'Head')
    tongue_obj.shape_key_add(name='Basis');key=tongue_obj.shape_key_add(name='OpenMouth')
    for p in key.data:p.co.y-=.075
    tube('Labio_superior',[(0,-1.353,1.0),(0,-1.346,.955)],.006,lip,'Head')
    sphere('Mochila',(0,.40,1.34),(.35,.40,.20),leather,20,12,'Bag')
    for i in range(7):
        angle=i*2.4;start=(.18*math.cos(angle),.37+.16*math.sin(angle),1.46)
        end=(.40*math.cos(angle),.37+.36*math.sin(angle),1.60+random.uniform(.02,.16))
        leaf('Follaje_'+str(i),start,end,.085,green,'Bag')
    tube('Tallo_cabeza',[(0,-.57,1.55),(.015,-.57,1.69),(.025,-.57,1.82)],.012,green,'Leaf')
    leaf('Hoja_cabeza',(.02,-.57,1.69),(.27,-.56,1.94),.095,green,'Leaf')
    leaf('Hoja_pequena',(.01,-.57,1.67),(-.14,-.57,1.79),.05,green,'Leaf')
    bpy.context.view_layer.update()
    for o in parts:
        if o.data.materials and o.data.materials[0]==base:f.set_colors(o)
    for side in (-1,1):
        eye=bpy.data.objects['Ojo_'+str(side)];eye.shape_key_add(name='Basis');key=eye.shape_key_add(name='Blink')
        for v,p in zip(eye.data.vertices,key.data):p.co.z=v.co.z*.025;p.co.y+=.062
    for o in parts:
        if o.data.shape_keys:
            for key in list(o.data.shape_keys.key_blocks)[1:]:key.value=0
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.06));ground=bpy.context.object;ground.name='Suelo_estudio';ground.data.materials.append(mat('Suelo',(.035,.055,.047)))
    for name,pos,power,size,color in [('Key',(2,-4,5),550,4,(1,.89,.74)),('Fill',(-3,-2,3),230,3,(.75,.85,1)),('Rim',(1,3,4),550,3,(1,.78,.48))]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=size;data.color=color;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=pos;aim(o,(0,0,1))
    data=bpy.data.cameras.new('Camera');o=bpy.data.objects.new('Camera',data);s.collection.objects.link(o);o.location=(3.2,-4.5,2.65);aim(o,(0,-.04,.99));data.type='ORTHO';data.ortho_scale=3.45;s.camera=o
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'08-cuy-aventurero-base.blend'));result=f.stats(parts);result['render_seconds']=f.render('08-cuy-aventurero-base')

elif a.stage=='groom':
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'08-cuy-aventurero-base.blend'));s=setup()
    surfaces=[o for o in bpy.data.collections['CUY_personaje'].objects if o.name.startswith(('01_','02_','03_'))]
    data,cum,total=f.surface_data(surfaces);original_sample=f.sample
    def sample(*args):
        value=original_sample(*args)
        if not value:return None
        p,n,part=value
        for side in (-1,1):
            if (p-Vector((side*.34,-1.095,1.18))).length<.185:return None
        return value
    f.sample=sample
    cards=f.cards(2400,data,cum,total,f.card_material(f.alpha_atlas()),'Pelaje_cards_LOD0');cards.hide_render=True
    groups={'Body':([],[],[]),'Head':([],[],[])};count=0
    while count<70000:
        sample_value=sample(data,cum,total)
        if not sample_value:continue
        p,n,part=sample_value;bone='Body' if part.startswith('01_') else 'Head'
        positions,radii,colors=groups[bone]
        tangent=Vector((p.x*.25,1,-.17));tangent-=n*tangent.dot(n)
        if tangent.length<.01:tangent=n.orthogonal()
        tangent.normalize();cross=n.cross(tangent).normalized()
        length=random.uniform(.045,.100) if bone=='Body' else random.uniform(.035,.080)
        if part.startswith('03_'):length*=.38
        color=Vector(coat(p))*random.uniform(.87,1.09);jitter=random.uniform(-.24,.24)
        for t in (0,1/3,2/3,1):
            v=p+n*(-.001+length*t*.88)+tangent*(length*t*t*.40)+cross*(jitter*length*math.sin(t*math.pi/2))
            positions.extend(v);radii.append(.00095*(1-t*.94));colors.extend((*color,1))
        count+=1
    m=bpy.data.materials.new('Pelaje_hebras_Beauty');nodes=m.node_tree.nodes;links=m.node_tree.links;nodes.clear()
    output=nodes.new('ShaderNodeOutputMaterial');hair=nodes.new('ShaderNodeBsdfHairPrincipled');hair.parametrization='COLOR';hair.inputs['Roughness'].default_value=.58;hair.inputs['Radial Roughness'].default_value=.60
    attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='COAT';links.new(attr.outputs['Color'],hair.inputs['Color']);links.new(hair.outputs[0],output.inputs['Surface'])
    for bone,(positions,radii,colors) in groups.items():
        curves=bpy.data.hair_curves.new('Pelaje_'+bone);curves.add_curves([4]*(len(radii)//4));curves.attributes['position'].data.foreach_set('vector',positions)
        curves.attributes.new('radius','FLOAT','POINT').data.foreach_set('value',radii);curves.attributes.new('COAT','FLOAT_COLOR','POINT').data.foreach_set('color',colors);curves.materials.append(m)
        o=bpy.data.objects.new('Beauty_fur_'+bone,curves);s.collection.objects.link(o);o['bone']=bone
    s.render.resolution_x=1024;s.render.resolution_y=1024;s.cycles.samples=48
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'09-cuy-aventurero-pelaje.blend'));result={'strands':count,'cards':2400,'render_seconds':f.render('09-cuy-aventurero-pelaje')}

elif a.stage=='rig':
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'09-cuy-aventurero-pelaje.blend'));s=setup();col=bpy.data.collections['CUY_personaje']
    specs=[('Root',(0,0,.1),(0,0,.35),None),('Body',(0,.1,.60),(0,.1,.95),'Root'),('Head',(0,-.35,.95),(0,-.7,1.25),'Body'),('Bag',(0,.4,1.30),(0,.4,1.56),'Body'),('Leaf',(0,-.57,1.58),(.02,-.57,1.85),'Head')]
    for side in (-1,1):
        for y,label in [(-.63,'Front'),(.68,'Back')]:
            name=label+('_L' if side<0 else '_R');ankle=(side*.46,y,.19)
            specs.extend([('Leg_'+name,(side*.43,y,.52),ankle,'Body'),('Foot_'+name,ankle,(side*.46,y-.18,.14),'Leg_'+name)])
    guides=[]
    for bone,ys in [('Body',(-.05,.40,.85)),('Head',(-.95,-.55))]:
        for y in ys:
            for side in (-1,1):
                p=(side*.43,y,1.20 if bone=='Body' else 1.35);name='Fur_'+str(len(guides));guides.append((name,Vector(p),bone));specs.append((name,p,(p[0],p[1],p[2]+.12),bone))
    arm=bpy.data.armatures.new('Cuy_rig');rig=bpy.data.objects.new('Cuy_rig',arm);s.collection.objects.link(rig);rig.show_in_front=True
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
    for name,head,tail,parent in specs:
        b=arm.edit_bones.new(name);b.head=head;b.tail=tail
        if parent:b.parent=arm.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    cards=bpy.data.objects['Pelaje_cards_LOD0'];cards.hide_render=False
    for o in col.objects:
        if o.type!='MESH':continue
        if o==cards:
            for i in range(0,len(o.data.vertices),6):
                root=(o.data.vertices[i].co+o.data.vertices[i+1].co)/2;parent='Head' if root.y<-.35 else 'Body'
                candidates=[g for g in guides if g[2]==parent];guide=min(candidates,key=lambda g:(g[1]-root).length_squared)[0]
                for j in range(6):
                    weight=(j//2)/2
                    if weight<1:(o.vertex_groups.get(parent) or o.vertex_groups.new(name=parent)).add([i+j],1-weight,'REPLACE')
                    if weight>0:(o.vertex_groups.get(guide) or o.vertex_groups.new(name=guide)).add([i+j],weight,'REPLACE')
        else:
            group=o.vertex_groups.new(name=o.get('bone','Body'));group.add(list(range(len(o.data.vertices))),1,'REPLACE')
        mod=o.modifiers.new('Skin','ARMATURE');mod.object=rig
    for o in list(s.objects):
        if o.name.startswith('Beauty_fur_'):
            # Beauty groom follows its rigid region; game fur uses weighted guides.
            o.hide_render=True;o.hide_viewport=True
    states={name:[0.,0.] for name in ['Bag','Leaf']+[g[0] for g in guides]};dt=1/120
    s.frame_start=1;s.frame_end=72;s.render.fps=24
    for frame in range(1,73):
        t=(frame-1)/24;phase=t*2*math.pi*1.4
        body=rig.pose.bones['Body'];body.location=(0,0,.012*math.sin(phase*2));body.rotation_mode='XYZ';body.rotation_euler=(.025*math.sin(phase*2),0,.020*math.sin(phase))
        body.keyframe_insert('location',frame=frame);body.keyframe_insert('rotation_euler',frame=frame)
        head=rig.pose.bones['Head'];head.rotation_mode='XYZ';head.rotation_euler=(.025*math.sin(phase-.25),0,.035*math.sin(phase*.5));head.keyframe_insert('rotation_euler',frame=frame)
        for side in (-1,1):
            for label in ('Front','Back'):
                name=label+('_L' if side<0 else '_R');offset=(0 if side<0 else math.pi)+(math.pi if label=='Back' else 0)
                b=rig.pose.bones['Leg_'+name];b.rotation_mode='XYZ';b.rotation_euler.x=.32*math.sin(phase+offset);b.keyframe_insert('rotation_euler',frame=frame)
                b=rig.pose.bones['Foot_'+name];b.rotation_mode='XYZ';b.rotation_euler.x=-.17*math.sin(phase+offset);b.keyframe_insert('rotation_euler',frame=frame)
        for name,state in states.items():
            stiffness,damping,limit=(35,10,.16) if name=='Bag' else ((55,9,.28) if name=='Leaf' else (110,16,.14))
            for substep in range(5):
                time_now=t+substep*dt;force=(5 if name=='Bag' else 10)*math.sin(time_now*8+len(name)*.4)+2*math.sin(time_now*3)
                state[1]+=(force-stiffness*state[0]-damping*state[1])*dt;state[0]+=state[1]*dt
                state[0]=max(-limit,min(limit,state[0]))
            b=rig.pose.bones[name];b.rotation_mode='XYZ';b.rotation_euler.x=state[0];b.rotation_euler.z=state[0]*.35;b.keyframe_insert('rotation_euler',frame=frame)
        blink=max(0,1-abs(frame-22)/2) if frame<40 else max(0,1-abs(frame-56)/2)
        for side in (-1,1):
            key=bpy.data.objects['Ojo_'+str(side)].data.shape_keys.key_blocks['Blink'];key.value=blink;key.keyframe_insert('value',frame=frame)
        opening=max(0,math.sin((frame-30)/20*math.pi)) if 30<=frame<=50 else 0
        smile=max(0,min(1,(frame-35)/12)) if frame<60 else max(0,(72-frame)/12)
        for name in ('Expresion_boca','Lengua'):
            keys=bpy.data.objects[name].data.shape_keys.key_blocks;keys['OpenMouth'].value=opening;keys['OpenMouth'].keyframe_insert('value',frame=frame)
            if 'Smile' in keys:keys['Smile'].value=smile;keys['Smile'].keyframe_insert('value',frame=frame)
    s.frame_set(1)
    # Meaningful skin invariants before export.
    unweighted=0;bad_weights=0
    for o in col.objects:
        if o.type!='MESH':continue
        for v in o.data.vertices:
            total=sum(g.weight for g in v.groups)
            if not v.groups:unweighted+=1
            if abs(total-1)>1e-4:bad_weights+=1
    assert unweighted==0 and bad_weights==0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'10-cuy-aventurero-rig.blend'))
    # Preserve editable pieces in .blend; consolidate rigid skinned pieces for runtime.
    bpy.ops.object.select_all(action='DESELECT')
    rigid=[o for o in col.objects if o.type=='MESH' and o!=cards and not o.data.shape_keys]
    for o in rigid:o.select_set(True)
    bpy.context.view_layer.objects.active=rigid[0];bpy.ops.object.join();bpy.context.object.name='Cuy_skin_agrupado'
    bpy.ops.object.select_all(action='DESELECT')
    for o in col.objects:o.select_set(True)
    rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.export_scene.gltf(filepath=str(OUT/'cuy-aventurero.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='SCENE',export_anim_scene_split_object=False,export_force_sampling=True)
    s.render.resolution_x=512;s.render.resolution_y=512;s.cycles.samples=24
    result={'bones':len(specs),'fur_guides':len(guides),'unweighted_vertices':unweighted,'bad_weight_sums':bad_weights,'frames':72,'fps':24,'physics':'Damped angular springs baked into keys; no general collision solver or live engine integration','render_seconds':f.render('10-cuy-version-juego')}
elif a.stage=='preview':
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'10-cuy-aventurero-rig.blend'));s=setup();s.render.resolution_x=384;s.render.resolution_y=384;s.cycles.samples=12
    (OUT/'animacion').mkdir(parents=True,exist_ok=True)
    renders=[]
    for frame in (1,7,13,19,22,25,31,37,41,46,55,56,58,64,70,72):
        s.frame_set(frame);renders.append(f.render('animacion/frame-'+str(frame).zfill(3)))
    result={'frames_rendered':16,'total_render_seconds':round(sum(renders),3)}
(OUT/(a.stage+'-mediciones.json')).write_text(json.dumps(result,indent=2),encoding='utf-8');print('COMPLETE',json.dumps(result),flush=True)
