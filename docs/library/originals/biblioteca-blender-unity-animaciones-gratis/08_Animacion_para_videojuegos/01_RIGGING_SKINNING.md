# Rigging y skinning para personajes de videojuegos

## Preparación del mesh
- Verifica escala y orientación, origen y nombres coherentes.
- Usa topología que se deforme correctamente en hombros, codos, rodillas y cadera.
- Evita geometría duplicada, pesos sin normalizar y huesos innecesarios.
- Para un personaje humanoide, usa una jerarquía de huesos consistente y una pose de referencia documentada.

## Rigging en Blender
1. Crea un Armature y alinea las articulaciones.
2. Define jerarquías, simetría y convenciones de nombres.
3. Vincula el mesh al armature con pesos automáticos como punto de partida.
4. Corrige Weight Paint manualmente; prueba deformaciones extremas.
5. Revisa influencias por vértice y límites del hardware de destino.
6. Diferencia huesos de control y huesos de deformación antes de exportar.

## Pruebas mínimas
- Brazos arriba, flexión de codos, sentadilla, giro de torso y carrera.
- No hay colapsos de volumen graves, inversiones o vértices sueltos.
- El rig se exporta sin dependencias de constraints no horneados.

Documentación: https://docs.blender.org/manual/en/latest/animation/armatures/index.html
