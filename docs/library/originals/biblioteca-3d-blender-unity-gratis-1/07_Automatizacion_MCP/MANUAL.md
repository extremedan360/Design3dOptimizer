# Reglas para un agente automatizado Blender / MCP

## Contrato de salida
- Entregar .blend editable y FBX o glTF según pipeline aprobado.
- Nombres únicos, escala y pivotes consistentes.
- UV válidas, materiales asignados y texturas referenciadas.
- Generar variantes LOD cuando la escena lo justifique.
- Crear un reporte JSON de triángulos, objetos, materiales y texturas.
- Evitar geometría no-manifold salvo diseño intencional.
- No inventar presupuestos: solicitar perfil de dispositivo o usar objetivos configurables.

## Pseudovalidaciones
- Revisar dimensiones y transforms.
- Detectar materiales duplicados y texturas faltantes.
- Revisar normales, UV, triangulación y jerarquía de huesos.
- Exportar asset de prueba e importarlo en Unity.
- Marcar como pendiente toda prueba que requiera Unity real y no se haya ejecutado.
