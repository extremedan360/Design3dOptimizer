"""Inspect an unsigned NPZ surface in an isolated Blender process.

blender --background --factory-startup --python render_unsigned.py -- \
  --input repaired/surface.npz --outputfolder review --render

Optional neck relaxation is explicitly case-specific and disabled unless both
Y limits are supplied. It changes geometry, not merely shading. Use before UVs,
rigging or morphs; material/rig authoring is a later stage.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def render_views(obj, output, prefix, resolution=512, samples=8, threads=4):
    import bpy
    from mathutils import Vector
    scene = bpy.context.scene
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    low = Vector([min(p[i] for p in points) for i in range(3)])
    high = Vector([max(p[i] for p in points) for i in range(3)])
    center, size = (low + high) / 2, max(high - low)
    scene.world = scene.world or bpy.data.worlds.new('ReviewWorld')
    scene.world.color = (.06, .06, .06)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.max_bounces = 2
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = threads
    scene.render.resolution_x = scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    for location, factor in [((-2, -3, 4), 150), ((3, -1, 1), 70), ((0, 3, 3), 110)]:
        bpy.ops.object.light_add(type='AREA', location=center + Vector(location) * size)
        light = bpy.context.object
        light.data.energy = factor * size * size
        light.data.size = size * 3
        light.rotation_euler = (center - light.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = size * 1.17
    for name, direction in [('front', (0, -1, .1)), ('quarter', (1, -1, .5)),
                            ('side', (1, 0, .1)), ('back', (0, 1, .1)), ('top', (0, 0, 1))]:
        camera.location = center + Vector(direction).normalized() * size * 3
        camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(output / (prefix + '-' + name + '.png'))
        bpy.ops.render.render(write_still=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path, help='surface.npz from unsigned_repair.py')
    parser.add_argument('--outputfolder', '--output-folder', dest='outputfolder', required=True, type=Path)
    parser.add_argument('--object-name', default='Generated_body_unsigned')
    parser.add_argument('--prefix', default='body-surface')
    parser.add_argument('--neck-y-min', type=float)
    parser.add_argument('--neck-y-max', type=float)
    parser.add_argument('--feet-z-max', type=float, help='Protect all vertices at or below this Blender Z.')
    parser.add_argument('--protect-config', type=Path, help='JSON with smooth_protect_ellipsoids or protect_ellipsoids.')
    parser.add_argument('--torso-relax-weight', type=float, default=0, help='Optional weaker relaxation behind the neck interval; 0 disables it.')
    parser.add_argument('--smooth-iterations', type=int, default=12)
    parser.add_argument('--smooth-factor', type=float, default=.75)
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--resolution', type=int, default=512)
    parser.add_argument('--samples', type=int, default=8)
    parser.add_argument('--threads', type=int, default=4)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
    if (args.neck_y_min is None) != (args.neck_y_max is None):
        raise ValueError('Specify both neck Y limits, or neither.')
    if args.neck_y_min is not None and (args.neck_y_min >= args.neck_y_max or args.feet_z_max is None):
        raise ValueError('A neck interval and an explicit protected foot level are required.')
    import bpy
    import numpy as np
    source, out = args.input.resolve(), args.outputfolder.resolve()
    out.mkdir(parents=True, exist_ok=True)
    data = np.load(source, allow_pickle=False)
    vertices, faces = data['vertices'], data['faces']
    if not np.isfinite(vertices).all():
        raise ValueError('Nonfinite coordinates.')
    volume = float(np.einsum('ij,ij->i', vertices[faces[:, 0]], np.cross(vertices[faces[:, 1]], vertices[faces[:, 2]])).sum() / 6)
    if volume < 0:
        faces = faces[:, ::-1]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh = bpy.data.meshes.new(args.object_name)
    mesh.from_pydata(vertices.tolist(), [], faces.tolist())
    mesh.update()
    obj = bpy.data.objects.new(args.object_name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    protected = []
    if args.protect_config:
        config = json.loads(args.protect_config.read_text(encoding='utf-8'))
        protected = config.get('smooth_protect_ellipsoids', config.get('protect_ellipsoids', []))
    moved_region = 0
    if args.neck_y_min is not None:
        group = obj.vertex_groups.new(name='Explicit_neck_relaxation')
        width = args.neck_y_max - args.neck_y_min
        for v in mesh.vertices:
            x, y, z = v.co
            if z <= args.feet_z_max:
                continue
            if any(sum(((v.co[i] - e['center'][i]) / e['radii'][i]) ** 2 for i in range(3)) < 1 for e in protected):
                continue
            if args.neck_y_min < y < args.neck_y_max:
                weight = min(1, (y - args.neck_y_min) / (width * .3125)) * min(1, (args.neck_y_max - y) / (width * .3125))
            elif y >= args.neck_y_max and args.torso_relax_weight > 0:
                weight = args.torso_relax_weight
            else:
                continue
            group.add([v.index], weight, 'REPLACE')
            moved_region += 1
        modifier = obj.modifiers.new('Protected_neck_geometry_relaxation', 'SMOOTH')
        modifier.vertex_group = group.name
        modifier.factor, modifier.iterations = args.smooth_factor, args.smooth_iterations
        status = bpy.ops.object.modifier_apply(modifier=modifier.name)
        if 'FINISHED' not in status:
            raise RuntimeError('Neck smoothing did not finish.')
    for p in mesh.polygons:
        p.use_smooth = True
    material = bpy.data.materials.new('Matte_geometry_review')
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (.36, .36, .36, 1)
    bsdf.inputs['Roughness'].default_value = .8
    mesh.materials.append(material)
    if args.render:
        render_views(obj, out, args.prefix, args.resolution, args.samples, args.threads)
    bpy.ops.wm.save_as_mainfile(filepath=str(out / (args.prefix + '.blend')))
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(filepath=str(out / (args.prefix + '.glb')), export_format='GLB', use_selection=True, export_animations=False)
    coords = np.array([v.co[:] for v in mesh.vertices], dtype=np.float32)
    report = {'source': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'object': obj.name, 'vertices': len(mesh.vertices), 'faces': len(mesh.polygons),
              'neck_y_interval': [args.neck_y_min, args.neck_y_max], 'protected_foot_z': args.feet_z_max,
              'smooth_region_vertices': moved_region, 'torso_relax_weight': args.torso_relax_weight, 'protection_ellipsoids': protected,
              'bounds': {'min': coords.min(0).tolist(), 'max': coords.max(0).tolist()},
              'limits': 'Visual-review checkpoint, not anatomy, accessory fit, rig, engine or mobile-performance certification.'}
    (out / (args.prefix + '-report.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
