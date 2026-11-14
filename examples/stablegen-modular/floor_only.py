"""Conservative geometry-only floor checkpoint in an ISOLATED Blender process.

blender --background --factory-startup --python floor_only.py -- \
  --source generated.glb --outputfolder /path/to/checkpoint

No remesh, solidify, booleans, anatomical repairs or object replacement. Review
before proceeding: the planar detector can also match flat contact surfaces.
Use before UVs/rigging: this geometry-only example does not retain UV/material
attributes. It rejects skins/morphs rather than silently damaging them.
"""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--outputfolder', '--output-folder', dest='outputfolder', required=True, type=Path)
    parser.add_argument('--floor-z', type=float, help='Explicit Blender Z-up plane level; otherwise infer at outer XY bounds.')
    parser.add_argument('--floor-band', type=float, help='Maximum vertex distance from plane; default 0.00018 times XY span.')
    parser.add_argument('--outer-ratio', type=float, default=0.34, help='XY radius fraction used to sample a generated platform.')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
    import bpy
    import numpy as np
    source, out = args.source.resolve(), args.outputfolder.resolve()
    if source.suffix.lower() != '.glb':
        raise ValueError('This checkpoint expects a generated GLB.')
    target = out / 'postfloor.glb'
    if target == source:
        raise ValueError('Output must not overwrite the source.')
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if len(meshes) != 1 or any(o.type == 'ARMATURE' for o in bpy.context.scene.objects):
        raise ValueError('Use a single unrigged generated surface; do not silently discard other modules.')
    obj = meshes[0]
    if obj.data.shape_keys:
        raise ValueError('Run this before morphs/rigging.')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    mesh = obj.data
    mesh.calc_loop_triangles()
    vertices = np.empty(len(mesh.vertices) * 3, np.float32)
    mesh.vertices.foreach_get('co', vertices)
    vertices = vertices.reshape(-1, 3)
    faces = np.array([t.vertices[:] for t in mesh.loop_triangles], dtype=np.int32)
    midpoint = (vertices[:, :2].min(0) + vertices[:, :2].max(0)) / 2
    span = float(np.ptp(vertices[:, :2], axis=0).max())
    outer = np.maximum(abs(vertices[:, 0] - midpoint[0]), abs(vertices[:, 1] - midpoint[1])) > span * args.outer_ratio
    if not outer.any():
        raise ValueError('No outer plane sample; provide a suitable detector region.')
    floor_z = args.floor_z if args.floor_z is not None else float(np.median(vertices[outer, 2]))
    band = args.floor_band if args.floor_band is not None else span * 0.00018
    remove = np.all(abs(vertices[faces, 2] - floor_z) < band, axis=1)
    kept = faces[~remove]
    if not len(kept) or not remove.any():
        raise ValueError('Detector removed everything or nothing; review source and parameters.')
    used = np.unique(kept)
    remap = np.full(len(vertices), -1, np.int32)
    remap[used] = np.arange(len(used))
    coords = vertices[used]
    result = bpy.data.meshes.new('Generated_surface_postfloor')
    result.from_pydata(coords.tolist(), [], remap[kept].tolist())
    result.update()
    obj.data = result
    obj.name = 'Generated_surface_postfloor'
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'postfloor.blend'))
    bpy.ops.export_scene.gltf(filepath=str(target), export_format='GLB', use_selection=True, export_animations=False)
    report = {
        'source': source.name, 'floor_z': floor_z, 'floor_band': band,
        'source_vertices': len(vertices), 'source_triangles': len(faces),
        'removed_triangles': int(remove.sum()), 'vertices': len(coords), 'triangles': len(kept),
        'bounds': {'min': coords.min(0).tolist(), 'max': coords.max(0).tolist()},
        'coordinate_frame': 'Blender Z up after applying imported transforms',
        'operations': ['Remove nearly coplanar generated floor triangles only', 'Retain original coordinates of surviving vertices'],
        'limits': 'Not a clean-anatomy, watertightness, rig, material, modularity or performance approval. Review all sides before another operation.',
    }
    (out / 'postfloor-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
