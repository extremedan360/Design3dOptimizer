# Blender a Unity: exportación

## Blender
1. Define unidades y escala física.
2. Aplica transformaciones cuando corresponda, con cuidado en rigs.
3. Revisa pivote/origen, nombres, materiales, UV y normales.
4. Exporta FBX con selección de objetos adecuada y opciones de ejes verificadas mediante un modelo de prueba.

## Unity
1. Importa modelo y texturas.
2. Verifica dimensiones, orientación y posición de pivote.
3. Comprueba normal maps y shader del render pipeline (URP/HDRP/Built-in).
4. Configura compresión de texturas por plataforma.
5. Añade LOD y colliders si corresponde.
6. Prueba en build del dispositivo objetivo, no solo en editor.

## Errores frecuentes
Escala 100x, orientación incorrecta, materiales rosas, texturas no asignadas, normales invertidas, animaciones sin huesos o tangentes incompatibles.
