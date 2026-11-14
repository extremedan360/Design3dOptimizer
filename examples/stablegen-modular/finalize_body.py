"""Explicit-budget body checkpoint before accessories or rigging, isolated Blender.

blender --background --factory-startup --python finalize_body.py -- \
  --input review/body-surface.blend --outputfolder body --target-triangles 18000

A triangle target is a hypothesis, not a mobile FPS guarantee. Original dense
surface is never overwritten. Existing rigs/morphs are rejected before QEM.
"""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--outputfolder', '--output-folder', dest='outputfolder', required=True, type=Path)
    parser.add_argument('--object', help='Required if the input has several mesh objects.')
    parser.add_argument('--object-name', default='Generated_Body_Base')
    parser.add_argument('--prefix', default='body-base')
    parser.add_argument('--target-triangles', type=int, help='Explicit exploratory target; omit to keep dense geometry.')
    parser.add_argument('--allow-open', action='store_true', help='Diagnostic only: do not treat this as a closed-body approval.')
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--resolution', type=int, default=512)
    parser.add_argument('--samples', type=int, default=8)
    parser.add_argument('--threads', type=int, default=4)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
    if args.target_triangles is not None and args.target_triangles < 4:
        raise ValueError('Triangle target must be positive and meaningful.')
    import bpy
    import bmesh
    from mathutils import Vector
    source, out = args.input.resolve(), args.outputfolder.resolve()
    if source == out / (args.prefix + '.blend'):
        raise ValueError('Do not overwrite the dense source checkpoint.')
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    candidates = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if args.object:
        obj = bpy.data.objects.get(args.object)
        if obj not in candidates:
            raise ValueError('Named mesh was not found.')
    elif len(candidates) == 1:
        obj = candidates[0]
    else:
        raise ValueError('Choose one body mesh explicitly; do not drop other modules silently.')
    if obj.data.shape_keys or any(m.type == 'ARMATURE' for m in obj.modifiers):
        raise ValueError('QEM must run before rigging and morph authoring.')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.data.calc_loop_triangles()
    before = len(obj.data.loop_triangles)
    if args.target_triangles is not None and args.target_triangles < before:
        modifier = obj.modifiers.new('Explicit_exploratory_budget', 'DECIMATE')
        modifier.ratio = args.target_triangles / before
        modifier.use_collapse_triangulate = True
        status = bpy.ops.object.modifier_apply(modifier=modifier.name)
        if 'FINISHED' not in status:
            raise RuntimeError('QEM did not finish; do not relabel the original mesh as optimized.')
    obj.data.validate()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    volume = bm.calc_volume(signed=True)
    if volume < 0:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
        volume = bm.calc_volume(signed=True)
    boundary = sum(e.is_boundary for e in bm.edges)
    nonmanifold = sum(not e.is_manifold for e in bm.edges)
    if (boundary or nonmanifold) and not args.allow_open:
        bm.free()
        raise RuntimeError('The QEM result is not a closed manifold body; inspect the small boundaries before exporting.')
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    obj.name = args.object_name
    for p in obj.data.polygons:
        p.use_smooth = True
    obj.data.calc_loop_triangles()
    points = [v.co for v in obj.data.vertices]
    low = Vector([min(p[i] for p in points) for i in range(3)])
    high = Vector([max(p[i] for p in points) for i in range(3)])
    bpy.ops.wm.save_as_mainfile(filepath=str(out / (args.prefix + '.blend')))
    bpy.ops.export_scene.gltf(filepath=str(out / (args.prefix + '.glb')), export_format='GLB', use_selection=True, export_animations=False)
    bpy.ops.wm.obj_export(filepath=str(out / (args.prefix + '.obj')), export_selected_objects=True,
                          forward_axis='Y', up_axis='Z', export_materials=False)
    report = {'source': source.name, 'object': obj.name, 'source_triangles': before,
              'target_triangles': args.target_triangles, 'triangles': len(obj.data.loop_triangles),
              'vertices': len(obj.data.vertices), 'boundary_edges': boundary, 'nonmanifold_edges': nonmanifold,
              'signed_volume': volume, 'bounds': {'min': list(low), 'max': list(high), 'dimensions': list(high - low)},
              'coordinate_frame': 'Blender Z up, front -Y; transforms applied; local coordinates equal world',
              'rig': False, 'facial_controls': False,
              'limits': 'Before-accessory geometry checkpoint. Closed topology and a triangle target do not prove anatomical quality, deformation quality or mobile FPS.'}
    (out / (args.prefix + '-report.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if args.render:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from render_unsigned import render_views
        render_views(obj, out, args.prefix, args.resolution, args.samples, args.threads)


if __name__ == '__main__':
    main()
