"""Inspect GLB 2 structure. Not a complete glTF conformance validator."""
import argparse,json,struct
from pathlib import Path

def read_glb(path):
    raw=Path(path).read_bytes()
    if len(raw)<12:raise ValueError('Truncated GLB header')
    magic,version,length=struct.unpack_from('<4sII',raw)
    if magic!=b'glTF' or version!=2 or length!=len(raw):raise ValueError('Invalid GLB 2 header/length')
    pos=12;document=None;binary=b''
    while pos<len(raw):
        if pos+8>len(raw):raise ValueError('Truncated chunk header')
        size,kind=struct.unpack_from('<II',raw,pos);pos+=8
        if size%4 or pos+size>len(raw):raise ValueError('Invalid chunk length/alignment')
        payload=raw[pos:pos+size];pos+=size
        if kind==0x4E4F534A:
            if document is not None:raise ValueError('Duplicate JSON chunk')
            document=json.loads(payload.decode('utf-8').rstrip(' \0'))
        elif kind==0x004E4942:binary=payload
    if document is None:raise ValueError('Missing JSON chunk')
    return document,binary

def report(path):
    doc,blob=read_glb(path);accessors=doc.get('accessors',[])
    triangles=0;vertices=0;primitives=0;morphs=[]
    for mesh in doc.get('meshes',[]):
        morphs.extend(mesh.get('extras',{}).get('targetNames',[]))
        for primitive in mesh['primitives']:
            primitives+=1;count=accessors[primitive['attributes']['POSITION']]['count'];vertices+=count
            indices=accessors[primitive['indices']]['count'] if 'indices' in primitive else count
            mode=primitive.get('mode',4)
            if mode==4:triangles+=indices//3
            elif mode in (5,6):triangles+=max(0,indices-2)
    animations=[]
    for anim in doc.get('animations',[]):
        samplers=anim.get('samplers',[]);ends=[accessors[s['input']].get('max',[0])[0] for s in samplers]
        starts=[accessors[s['input']].get('min',[0])[0] for s in samplers]
        animations.append({'name':anim.get('name'),'channels':len(anim.get('channels',[])),
            'duration_seconds':round(max(ends,default=0)-min(starts,default=0),4),
            'target_paths':sorted({c['target']['path'] for c in anim.get('channels',[])})})
    return {'file':Path(path).name,'bytes':Path(path).stat().st_size,'meshes':len(doc.get('meshes',[])),
        'mesh_primitives':primitives,'exported_vertices_across_primitives':vertices,'triangles':triangles,
        'materials':len(doc.get('materials',[])),'images':len(doc.get('images',[])),
        'material_alpha_modes':[m.get('alphaMode','OPAQUE') for m in doc.get('materials',[])],
        'skins':len(doc.get('skins',[])),'joint_counts':[len(s['joints']) for s in doc.get('skins',[])],
        'morph_names':sorted(set(morphs)),'animations':animations,'cameras':len(doc.get('cameras',[])),
        'scope':'Structural inspection; no FPS, visual, collision or complete conformance validation'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('file');parser.add_argument('--output');args=parser.parse_args()
    try:result=report(args.file)
    except (OSError,ValueError,KeyError,IndexError,struct.error) as e:parser.exit(1,str(e)+'\n')
    text=json.dumps(result,indent=2,ensure_ascii=False)
    if args.output:Path(args.output).write_text(text,encoding='utf-8')
    print(text)
