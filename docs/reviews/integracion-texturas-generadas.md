# Integración de texturas generadas: autoridad visual y memoria

Revisión del 13 de noviembre de 2026. Método generalizado de un ensayo autorizado; no se redistribuyen sus recursos. [Ejemplo por etapas](../../examples/stablegen-sd15-staged/README.md) y [medidas resumidas](../evidencias/sd15-staged/resumen.json).

## Encontrar la autoridad visual

Seguir la construcción hasta después del arranque: quién crea la malla visible, oculta la anterior y modifica materiales. Un recurso importado correcto puede quedar reemplazado posteriormente. Ocultar renderers tampoco libera sus recursos. Compactar índices y vértices por grupo evita duplicaciones, pero exige medirlas; tres renderers no garantizan tres draws ni FPS.

Un pase artístico puede sustituir una textura de autor por otra procedural. Renombrar el material para esquivarlo también puede romper su pertenencia a la paleta. Separar ambas responsabilidades: conservar explícitamente el mapa, manteniendo recoloreado y desgaste. Comprobar arranque, reaplicación de estilo y cambios de estado, sin reasignar texturas cada fotograma.

Una prueba dirigida en Play del Editor conservó el mapa y la paleta en día y noche sobre un objeto de tres renderers y 2.860 triángulos; se comprobó una superficie de asiento a 0,62 m. No acredita todas las interacciones corporales, normales, respuesta PBR o rendimiento. La preparación falló primero por un identificador de metadatos mal formado, no por la importación de la malla; se corrigió conservando el original. Las mejoras de normales derivadas de imagen siguen preparadas, sin ejecutar: no son mediciones físicas del material.

## RAM y VRAM son presupuestos distintos

Equipo observado: Windows, RTX 3050 Ti de 4.096 MiB y 16 GB de RAM. Grafo común procedente de StableGen, adaptado a SD1.5 FP16: 512×512, lote 1, 20 pasos, Euler y CFG 5,5. Un nombre histórico del constructor no cambia la arquitectura real.

| Carga monolítica | Duración hasta parada | GPU total máxima observada | RAM disponible mínima |
| --- | ---: | ---: | ---: |
| Habitual | 19,78 s | 2.069 MiB | 1.759 MiB |
| Tras liberar RAM | 13,44 s | 400 MiB | 2.004 MiB |
| Dinámica respaldada por disco | 12,52 s | 400 MiB | 1.292 MiB |

Los tres intentos cruzaron la guardia de RAM y no produjeron imagen completa. Se conservaron umbrales de 2 GiB disponibles y 3.600 MiB de GPU total. El monitor muestrea cada 0,75 s más consultas: puede perder picos y reaccionar tarde. GPU total incluye otros procesos; las guardias no son límites físicos estrictos.

## Separar componentes y comprobar cada etapa

La partición por streaming verificó byte a byte 1.145 tensores F16: 197 de texto, 686 de difusión, 248 de VAE y 14 auxiliares preservados. No hubo entrenamiento ni cuantización; el original quedó intacto. Cada proceso cargó sólo su componente. Condicionamientos y latente se intercambiaron mediante safetensors CPU con estructura tipada, límites y recibos SHA, sin pickle. Se conservó el marcador nativo de escala del latente.

| Etapa | Tiempo del monitor | GPU total máxima | RAM disponible mínima | Resultado |
| --- | ---: | ---: | ---: | --- |
| Texto en GPU | 15,703 s | 722 MiB | 4.264.177.664 B | Ejecución correcta |
| Muestreo en GPU | 18,516 s | 2.259 MiB | 3.949.715.456 B | Latente guardado |
| VAE CPU, bloques 128/solape 32 | 60,329 s | 314 MiB | 4.379.430.912 B | Ejecución correcta; imagen rechazada |
| VAE CPU completo | 19,000 s | 314 MiB | 3.876.208.640 B | Primera textura aceptable |

El decode por bloques produjo discontinuidades visibles. Se decodificó **el mismo latente** completo, sin repetir muestreo ni cambiar semilla: desaparecieron los artefactos de mosaico observados. La comparación aísla el decode, sin garantizar identidad entre dispositivos o versiones.

Los primeros indicadores de cierre fueron falsos porque el lanzador no esperaba a su hijo. La auditoría posterior confirmó todos los procesos propios cerrados; se preservaron esos indicadores y se corrigió la espera. No se repitió inferencia para corregir el informe.

## Compatibilidad y alcance

El aviso específico de proyección de texto ausente se contrastó con el guardado SD1.5 y `return_projected_pooled=False`: no justificaba inventar pesos. Revisar cualquier otro aviso individualmente; conservar esta explicación junto al [código de referencia](https://github.com/Comfy-Org/ComfyUI/blob/c1eece62cbf1805d4f64286d7f5592e6a215e6ba/comfy/sd1_clip.py).

Son resultados locales, no garantía para cualquier GPU de 4 GB, panel completo StableGen, SDXL, multivista o juego final. Evaluar también continuidad, paleta, escala, luz y coste en motor. Los pesos SD1.5 conservan CreativeML OpenRAIL-M; [StableGen](https://github.com/sakalond/StableGen) conserva GPL-3.0 y las utilidades originales de esta biblioteca MIT, sin relicenciar dependencias ni pesos.
