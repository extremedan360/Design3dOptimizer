"""Inventory independent meshes and attachment metadata in an isolated Blender.

blender --background --factory-startup --python-exit-code 2 --python
scripts/modular_report.py -- --file asset.glb --output report.json
Does not save the scene. Object separation does not certify semantic independence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy


def report(source):
    source = Path(source).resolve()
    if source.suffix.lower() == '.blend':
        bpy.ops.wm.open_mainfile(filepath=str(source))
    elif source.suffix.lower() == '.glb':
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(source))
    else:
        raise ValueError('Expected .blend or .glb')
    rows = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            rows.append({
                'name': obj.name,
                'parent': obj.parent.name if obj.parent else None,
                'parent_type': obj.parent_type,
                'parent_bone': obj.parent_bone,
                'collections': sorted(c.name for c in obj.users_collection),
                'vertices_evaluated': len(mesh.vertices),
                'triangles_evaluated': len(mesh.loop_triangles),
                'materials': [s.material.name if s.material else None for s in obj.material_slots],
                'morphs': [k.name for k in obj.data.shape_keys.key_blocks] if obj.data.shape_keys else [],
                'armatures': [m.object.name for m in obj.modifiers if m.type == 'ARMATURE' and m.object],
                'shared_mesh_users': obj.data.users,
            })
        finally:
            evaluated.to_mesh_clear()
    return {
        'file': source.name,
        'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'blender': bpy.app.version_string,
        'frame': bpy.context.scene.frame_current,
        'mesh_objects': len(rows),
        'triangles_evaluated': sum(r['triangles_evaluated'] for r in rows),
        'objects': rows,
        'limits': 'Inventory at the current frame, including visible and hidden meshes. Does not certify fit, winding, collisions, appearance, engine cost or mobile FPS.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    target = Path(args.output).resolve()
    if target == Path(args.file).resolve():
        raise ValueError('Report must not overwrite the asset')
    result = report(args.file)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('MODULAR_INVENTORY_OK', result['mesh_objects'], result['triangles_evaluated'])
