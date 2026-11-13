"""Import the actual GLB and check skin, morphs and motion in a clean scene."""
import bpy,sys,argparse,json,math,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from glb_report import read_glb
parser=argparse.ArgumentParser();parser.add_argument('--file',required=True);parser.add_argument('--output',required=True);parser.add_argument('--render',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(Path(args.file).resolve()))
s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE')
# Blender's importer may add a local bone-display Icosphere absent from the GLB.
helpers={p.custom_shape for p in rig.pose.bones if p.custom_shape}
meshes=[o for o in s.objects if o.type=='MESH' and o not in helpers]
for helper in helpers:bpy.data.objects.remove(helper,do_unlink=True)
doc,_=read_glb(args.file)
assert len(meshes)==sum('mesh' in node for node in doc['nodes'])
assert len(rig.data.bones)==len(doc['skins'][0]['joints'])
assert all(name in rig.data.bones for name in ('Root','Body','Head','Bag','Leaf','Fur_0','Leg_Front_L'))
samples=[];bad=0;unweighted=0;finite=True
for o in meshes:
    for v in o.data.vertices:
        finite &= all(math.isfinite(c) for c in v.co)
        weight=sum(g.weight for g in v.groups)
        unweighted+=weight<1e-6;bad+=abs(weight-1)>1e-4
assert finite and bad==0 and unweighted==0
for frame in (1,22,40,56,72):
    s.frame_set(frame)
    sample={'frame':frame,'morphs':{},'secondary_matrices':{}}
    for o in meshes:
        if o.data.shape_keys:sample['morphs'][o.name]={k.name:round(k.value,4) for k in o.data.shape_keys.key_blocks if k.name!='Basis'}
    for bone in ('Bag','Leaf','Fur_0','Leg_Front_L'):
        sample['secondary_matrices'][bone]=[round(x,6) for row in rig.pose.bones[bone].matrix for x in row]
    samples.append(sample)
blink=max(d.get('Blink',0) for sample in samples for d in sample['morphs'].values())
opening=max(d.get('OpenMouth',0) for sample in samples for d in sample['morphs'].values())
smile=max(d.get('Smile',0) for sample in samples for d in sample['morphs'].values())
print('MORPH_SAMPLES',json.dumps([(x['frame'],x['morphs']) for x in samples]),flush=True)
assert blink>.9 and opening>.9 and smile>.9
for bone in ('Bag','Leaf','Fur_0','Leg_Front_L'):
    assert len({tuple(sample['secondary_matrices'][bone]) for sample in samples})>1,bone
result={'source_sha256':hashlib.sha256(Path(args.file).read_bytes()).hexdigest(),'roundtrip_pass':True,'mesh_objects':len(meshes),'bones':len(rig.data.bones),'unweighted_vertices':unweighted,'non_normalized_vertices':bad,'finite_coordinates':finite,'max_blink':blink,'max_open_mouth':opening,'max_smile':smile,'samples':samples,
        'scope':'Blender reimport and sampled animation; not a continuous collision/engine performance test'}
(out/'roundtrip.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
if args.render:
    s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.cycles.max_bounces=4;s.cycles.transparent_max_bounces=12
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='CUDA'
    s.cycles.device='GPU';s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100
    s.world.color=(.24,.24,.24)
    def aim(o):o.rotation_euler=(Vector((0,-.04,.99))-o.location).to_track_quat('-Z','Y').to_euler()
    for name,pos,energy,size in [('Key',(2,-4,5),550,4),('Fill',(-3,-2,3),230,3),('Rim',(1,3,4),550,3)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.size=size;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=pos;aim(o)
    data=bpy.data.cameras.new('Review');o=bpy.data.objects.new('Review',data);s.collection.objects.link(o);o.location=(3.2,-4.5,2.65);data.type='ORTHO';data.ortho_scale=3.45;aim(o);s.camera=o
    for name,frame in [('neutral',1),('blink',22),('open',40),('smile',55)]:
        s.frame_set(frame);s.render.filepath=str(out/('imported-'+name+'.png'));bpy.ops.render.render(write_still=True)
print('ROUNDTRIP_PASS',json.dumps({k:v for k,v in result.items() if k!='samples'}),flush=True)
