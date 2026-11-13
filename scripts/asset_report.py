"""Blender read-only asset inventory; excludes no objects implicitly."""
import bpy,sys,json,argparse,math
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
result={'blender':bpy.app.version_string,'frame':bpy.context.scene.frame_current,'objects':[],
        'scope':'Whole scene inventory, not a production/gameplay approval'}
deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
    item={'name':o.name,'type':o.type,'hide_render':o.hide_render}
    if o.type=='MESH':
        evaluated=o.evaluated_get(deps);mesh=evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles();item['evaluated_vertices']=len(mesh.vertices);item['evaluated_triangles']=len(mesh.loop_triangles)
            item['finite_coordinates']=all(math.isfinite(c) for v in mesh.vertices for c in v.co)
        finally:evaluated.to_mesh_clear()
        item['materials']=[m.name if m else None for m in o.data.materials]
        item['morphs']=list(o.data.shape_keys.key_blocks.keys()) if o.data.shape_keys else []
        if any(m.type=='ARMATURE' for m in o.modifiers):
            weights=[sum(g.weight for g in v.groups) for v in o.data.vertices]
            item['unweighted_vertices']=sum(w<1e-6 for w in weights)
            item['non_normalized_vertices']=sum(abs(w-1)>1e-4 for w in weights)
    elif o.type=='ARMATURE':item['bones']=len(o.data.bones)
    elif o.type=='CURVES':item['curves']=len(o.data.curves);item['curve_points']=len(o.data.points)
    result['objects'].append(item)
result['images']=[{'name':i.name,'size':list(i.size)} for i in bpy.data.images if i.type=='IMAGE']
Path(args.output).write_text(json.dumps(result,indent=2),encoding='utf-8')
print('ASSET_REPORT_WRITTEN',Path(args.output).name)
