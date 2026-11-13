# Materiales, complementos y exportación: lecciones medidas

Ensayos locales del 2026-11-12, Blender 5.2.3 LTS, GPU de 4 GB y 16 GB RAM. Se documentan procedimientos y límites, sin distribuir los modelos, imágenes de referencia o diseños privados.

## Diseñar en orden y con función

Primero revisar la base sin ropa ni accesorios; después integrar una pieza por etapa. La sujeción forma parte del diseño: colocar el pivote en el apoyo real, reservar movimiento de las articulaciones y adaptar correas/arnés al tipo de personaje. La guía mantenida está en [modelado](../../.agents/skills/design3d-optimizer/references/modelado.md). Esta revisión no sustituye observar poses con cada accesorio colocado.

Una mochila independiente de prueba se agrupó en cuatro mallas/materiales: tela, cuero, metal y detalles por vértice. Se midieron 7.002 triángulos y cuatro imágenes de 256² para color/normal de tela y cuero. El bloque principal, solapa, bolsillos, asa, hebilla, correas y costuras aportan lectura a distintas distancias; no hace falta geometría para cada poro del cuero. Su render aislado observó 773,7 MiB RAM de Blender y 671 MiB GPU global. Estas cifras no prueban rendimiento del conjunto ni del motor.

Los bordados/costuras pequeños se marcaron para omitir a distancia, conservando el volumen principal. Las piezas rígidas usan un hueso de accesorio; las puntas y colgantes que necesiten movimiento deben tener su propia solución. Una animación horneada de prueba no es física interactiva.

## Cuero, tela y color

- Separar respuesta de materiales: tela mate con trama fina; cuero con grano irregular y reflexión moderada; metal con rugosidad y metalicidad propias. No lograr cuero solo cambiando el color de una superficie plástica.
- Mantener geometría para silueta, dobleces, solapa y herrajes visibles; usar imágenes/normales para microdetalle. Comprobar cruces tela-solapa también desde arriba: una vista frontal puede ocultar una penetración.
- No reducir un atlas corporal completo y reutilizarlo como un tile de cuero: mezcla islas y puede introducir blanco o pelo en los bolsillos. Un tile específico elimina esa dependencia.
- Distinguir valores lineales, imágenes byte sRGB e imágenes Non-Color. Probar el PNG guardado y el material reimportado; una conversión gamma duplicada u omitida cambia el acabado.
- `image.pixels.foreach_set` requiere datos compatibles; un array NumPy float64 produjo `incorrect sequence item type: d`. Convertir explícitamente a float32 antes de escribir. No modificar bibliotecas globales para resolverlo.
- Si el albedo ya contiene COAT horneado, no exportar también COLOR_0 corporal multiplicándolo otra vez. Conservar el atributo en autoría y retirarlo solo de las copias de exportación. Pelaje y bordado pueden necesitar COLOR_0 de forma intencional.

## Ojos y párpados

Una esfera negra con un gran reflejo uniforme puede perder lectura. Ajustar volumen, pupila/iris, rugosidad, IOR y tamaño/posición de las luces de forma conjunta. Un cambio de iluminación no demuestra una mejora de geometría; comparar también con el mismo estudio.

Se probó un ojo estilizado oscuro con un iris periférico discreto, textura compartida de 256², IOR 1,40 y rugosidad 0,15. Son parámetros del ensayo, no una receta universal. El reflejo proviene de la iluminación, sin un punto blanco fijo en el albedo.

El cierre necesita revisar abierto, parcial y cerrado. La solución probada combinó un morph de párpado, retracción del globo `B**2.4` y correctivo intermedio `4*B*(1-B)`, con B entre cero y uno. Si el motor controla los morphs directamente, reproducir esa relación o las curvas horneadas. El correctivo no debe suponerse igual a uno en cualquier fotograma parcial: depende del valor real de B.

## Skin, LOD y glTF

Un primer conjunto exportado tuvo 13 huesos, máximo cuatro influencias normalizadas, 6.500 tarjetas en LOD0, 3.250 en LOD1 y ninguna en LOD2. El cuerpo de esa versión tuvo 42.546 / 21.272 / 7.444 triángulos; los totales con cara/pelo fueron 70.910 / 36.636 / 9.808. Todos los cuerpos se comprobaron cerrados. Los tamaños GLB fueron aproximadamente 5,85 / 3,84 / 1,97 MiB. No extrapolar esos tamaños al recurso modificado después.

Las tarjetas heredaron pesos de su raíz por interpolación baricéntrica sobre el triángulo corporal más cercano, con una misma combinación para los seis vértices de cada tarjeta. No equivale a física de puntas. Las costuras pegadas a una superficie deformable pueden transferir pesos; un equipo rígido independiente necesita un único anclaje rígido o una jerarquía propia.

Se reimportó **LOD0 de esa versión inicial** y se revisaron neutro, parpadeo y pose. Se conservaron los 13 huesos, seis componentes Blink y dos correctivos BlinkMid; no hubo vértices sin peso ni sumas inválidas. No se afirma que los tres LOD de la revisión posterior hayan completado esa prueba.

Inspeccionar el JSON glTF: triángulos, primitivas, skins, morph targets, canales, imágenes, alphaMode y extensiones. Se verificaron MASK para pelo y KHR_texture_transform para la escala UV del normal; el destino también debe soportar KHR_materials_ior y KHR_materials_specular si se utilizan. Un atributo de autoría que desactive sombras no es una configuración de sombras universal del motor.

Unir por material puede reducir objetos/primitivas, pero no demuestra draw calls o FPS. Mantener copia editable, generar LOD en copias, limitar influencias después de decimar y volver a reimportar cada variante final. No aplicar decimate/remesh indiscriminadamente sobre objetos con morphs.

## Estado y límites al cerrar el ensayo

Se verificaron la generación por etapas, reparación volumétrica local, retopología cerrada del cuerpo y renders de la nueva pieza independiente. Después de cambiar el cuerpo/accesorio, la revisión final del rig, los LOD y el motor seguía pendiente. Una pieza vegetal laminar se adelgazó en la ruta de suavizado/QuadriFlow; se detectó visualmente y no se considera resuelta. La recomendación pendiente de probar es separarla y controlar su espesor fuera de la retopología corporal.

Los detalles normales demasiado regulares o intensos produjeron bandas parecidas a una impresión 3D; se descartó ese ajuste. Un cuerpo cerrado aún puede tener hondonadas, salientes o anatomía incorrecta. No usar equipo o pelo para ocultarlos. No se midieron FPS ni física interactiva y no hay un rig facial de boca/diálogo validado en esta revisión.
