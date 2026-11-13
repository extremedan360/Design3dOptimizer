# Revisión: DESIGN:OS 3D Blender

Fuente: [jangtrinh/design-os-3d-blender](https://github.com/jangtrinh/design-os-3d-blender), commit `de2eac837fba9161ff3f9173e932225c8e3db45b`. Inspección de archivos el 12 noviembre 2026. No se instalaron ni ejecutaron el servidor, sus generadores o sus pruebas. Las capacidades son declaradas/inspeccionadas, no una integración funcional comprobada.

## Qué es realmente

Un servidor MCP de Blender 5.2, conocimiento y habilidades de agentes, con énfasis en piezas paramétricas, dimensiones e impresión 3D. El README enumera cuatro herramientas: estado de runtime, consulta de conocimiento, validación de especificación de pieza y ejecución de una pasada de Blender. No equivale a cuatro artistas autónomos trabajando simultáneamente.

## Perfiles revisados

| Perfil / ruta | Responsabilidad | Utilidad para nosotros |
| --- | --- | --- |
| `.agents/skills/blender-agent-core` | Ejecución, revisión, contexto y comprobaciones | Separar ejecución exitosa de resultado correcto; una sola escritura por escena |
| `.agents/skills/blender-image-to-3d` | Referencia, proporciones y construcción progresiva | Inventario de rasgos visibles, cámaras comparables y revisión de identidad visual |
| `.agents/skills/blender-knowledge-workbench` | Catálogo y consulta de conocimiento | Leer solo referencias necesarias; distinguir fuente, método y adaptación |
| `.agents/skills/img2threejs` | Reconstrucción procedural Three.js | Jerarquías, pivotes y componentes; es otro entorno, no un groom/rig Blender listo |
| `skills/design-os-3d-blender` | Entrada portable al producto/MCP | Diagnóstico e instalación opcional para quien quiera usar ese producto |

Hay copias para distintos asistentes; no contarlas como equipos distintos ni copiar todos los espejos. Su presencia en archivos no demuestra instalación o descubrimiento en nuestra aplicación.

## Ideas generales útiles

- Acordar resultado y dimensiones/relaciones importantes antes del detalle.
- Planear objetos, jerarquía, posiciones, materiales, cámara y luces.
- Guardar etapas y comprobar postcondiciones concretas: objeto existe, bounds, triángulos, materiales o claves.
- No confiar solo en código de salida o un mensaje de transporte. Este mismo trabajo observó Blender terminando con 0 después de una excepción Python; se comprobó el artefacto/reporte.
- Comparar referencia y render a escala aparente similar; una imagen no revela lados ocultos.
- Evaluar movimiento entre extremos, no solo poses inicial/final.
- Mantener separado conocimiento, código, evidencia y decisiones. Una comprobación de estructura no es aprobación visual, física o mecánica.

Son criterios generales documentados con redacción propia; no se trasladó su runtime ni se replicó el contrato propietario de su producto.

## Qué no adoptar automáticamente

- El propósito por defecto «impresión y render», unidades contractuales en mm y requisitos de paredes/manifold no corresponden por defecto a un personaje de juego.
- Sus aprobaciones y restricciones particulares no reemplazan instrucciones del usuario o permisos del entorno.
- Las cifras de rendimiento de su máquina no sirven como presupuesto de esta GPU.
- El propio README limita escultura orgánica y rigging de personajes complejo. No contiene una solución ya comprobada para nuestra mochila, parpadeo o pelaje interactivo.
- El MCP local y su addon son opcionales; nuestra prueba usa Blender CLI por etapas y no necesita instalarlos.

## Licencias y estado

El [LICENSE principal](https://github.com/jangtrinh/design-os-3d-blender/blob/de2eac837fba9161ff3f9173e932225c8e3db45b/LICENSE) declara PolyForm Shield 1.0.0 e incluye cláusula de no competencia. El subcomponente `img2threejs` declara Apache-2.0 en su archivo propio. Son ámbitos diferentes; no tratar el repositorio completo como MIT ni asumir que la licencia de una subcarpeta cubre el resto.

Esta revisión publica referencias y conclusiones propias. No se incorpora código, perfiles, plantillas, assets ni configuración de ese upstream. Una futura incorporación de software requiere decidir su alcance y revisar la licencia aplicable antes de copiar o distribuir.
