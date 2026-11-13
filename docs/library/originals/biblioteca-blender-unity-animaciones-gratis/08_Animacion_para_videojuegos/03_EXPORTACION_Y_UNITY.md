# Pipeline de animación Blender → Unity

## Antes de exportar
1. Aplica y comprueba transformaciones cuidadosamente, sin romper el rig.
2. Define pose base, escala y ejes de exportación.
3. Decide si exportar mesh+rig+clips juntos o animaciones separadas.
4. Hornea animaciones dependientes de constraints/control rigs cuando haga falta.
5. Evita exportar huesos de control innecesarios.

## FBX
- Exporta únicamente los objetos previstos.
- Incluye armature, mesh y acciones necesarias; verifica opciones Bake Animation y NLA/All Actions según tu estrategia.
- Haz una prueba con un personaje y dos clips antes de procesar lotes.

## Unity
1. Importa FBX en `Assets/Art/Characters/`.
2. Configura Rig: Humanoid (si aplica y mapea bien) o Generic.
3. Verifica Avatar y pose de referencia.
4. En Animation, comprueba nombres, intervalos, looping y root transforms.
5. Crea Animator Controller y prueba las transiciones en Play Mode.
6. Comprueba que el mesh no se deforme, gire ni cambie de escala inesperadamente.

Fuentes: https://docs.unity3d.com/Manual/AnimationOverview.html ; https://docs.blender.org/manual/en/latest/addons/import_export/scene_fbx.html
