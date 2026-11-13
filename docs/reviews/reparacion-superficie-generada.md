# Reparar una superficie generada antes de reducirla

Ensayo local del 2026-11-12, Blender 5.2.3 LTS, NumPy/SciPy y scikit-image 0.25.2. Equipo: 16 GB RAM y GPU de 4 GB. Conocimiento general del procedimiento; no se distribuyen la referencia ni el modelo privados.

## Problema y decisión

Una salida de generación de 2.951.728 triángulos presentaba paredes interiores, 144.504 bordes abiertos y 378.008 aristas compartidas por más de dos caras. QEM directo y remalla con signo produjeron huecos o piezas parecidas a papel. Suavizar normales no repara esos defectos.

El método que funcionó en este caso fue reconstruir primero un volumen por ocupación **sin signo**, evitando depender del winding o de las normales de las caras originales. No es una reparación universal: cambia el contorno y puede cerrar cavidades intencionadas.

1. Rasterizar todos los triángulos mediante muestras baricéntricas en una rejilla ajustada al bounding box. Mantener escala y transformación para transferir materiales después.
2. Cierre morfológico de la superficie ocupada y relleno de volúmenes encerrados. Inspeccionar las componentes antes de descartar ninguna.
3. Filtrado gaussiano y extracción con marching cubes.
4. Revisar visualmente contorno, orejas, pies y accesorios. Comprobar bordes, degenerados y volumen; un resultado manifold todavía puede tener mal diseño.
5. QuadriFlow sobre la superficie sana, seguido de suavizado por regiones y transferencia de material.

## Parámetros y resultados observados

La rejilla tuvo 320 celdas en el eje largo, dimensiones 162 × 178 × 320 y 9.227.520 celdas totales. Paso 0,003127 unidades; cierre de 5 vóxeles y sigma 0,6. La reconstrucción tardó 4,251 s y produjo 341.444 triángulos sin bordes abiertos, aristas no manifold ni triángulos degenerados. Solo se descartaron dos vóxeles de componentes aisladas.

Ese paso ocupó unos 0,01564 en la escala del modelo: resulta demasiado agresivo para dedos separados o cavidades finas. Orejas, hojas y mochila necesitan inspección; mantener solo el volumen mayor perdería cualquier accesorio realmente separado. La primera medición de RSS tomó por error el lanzador de un entorno virtual en Windows: se descartó, se corrigió la búsqueda de descendientes y no se publica como consumo de la reparación.

QuadriFlow con objetivo de 22.000 caras produjo 21.269 quads y ocho pequeños huecos triangulares. Se cerraron únicamente sus componentes de borde, tras medir su tamaño; no se aplicó un relleno indiscriminado a cualquier apertura. Resultado: 21.267 vértices, 21.277 caras, 42.546 triángulos, cero bordes abiertos y cero aristas no manifold. Los polos automáticos no equivalen a loops faciales hechos para diálogo.

Suavizado ponderado conservó pies, nariz, orejas y vegetación. UV y horneado de albedo/rugosidad a 1024² permitieron desacoplar el aspecto de la densidad del original. El caché de material estaba en otro marco espacial: se convirtió al mismo sistema antes de interpolar. También se retiraron del albedo los ojos y brillos pintados donde iban ojos físicos nuevos, para evitar pupilas o reflejos duplicados.

## Pelaje y párpados sin depender del render de presentación

La prueba usa 6.500 tarjetas cortas, dos quads por tarjeta, 26.000 triángulos en total, atlas de máscara 512 × 256 y normales de raíz transferidas. Se excluyen ojos, nariz, plantas y regiones verdes; las máscaras de exclusión deben revisarse también en las orejas. El microdetalle normal complementa la silueta, no la sustituye. Tarjetas superpuestas pueden costar mucho fill rate aunque su malla sea pequeña; validar mipmaps, alpha clipping y sombras en el motor.

Los párpados se ajustaron a la superficie con BVH. La interpolación entre abierto y cerrado atravesaba el globo a mitad del parpadeo: un correctivo intermedio y una retracción gradual del ojo lo resolvieron en las vistas probadas. Se comprobaron 0, 0,5 y 1; no basta mirar los extremos. Es una solución estilizada, no anatomía ocular completa.

En una pasada inicial de estas tarjetas reales, sin curvas de pelo añadidas para presentación, se observaron 1.432,1 MiB de working set de Blender y 735 MiB de memoria GPU global. El horneado separado registró 935,0 MiB y 693 MiB, respectivamente. Muestreo aproximado cada 0,5 s más el coste de nvidia-smi; puede perder picos y GPU incluye otras aplicaciones. No son FPS, memoria del motor ni garantía de calidad para cualquier personaje.

Una máscara basada solo en verde dejó pelo sobre hojas amarillas y accesorios marrones. La revisión superior/trasera llevó a combinar región anatómica, color de origen y un KDTree de vértices prohibidos: rechazar raíces si el alcance completo de la tarjeta invade el margen, y comprobar también puntas/centros. Heredar el color de la raíz evita que la punta tome el verde de un accesorio cercano. Una región geométrica demasiado amplia dejó el lomo sin pelo: segmentar la mochila dentro de su región, en lugar de excluir todo el lomo. Los límites numéricos de color son específicos del recurso, no un segmentador universal.

Nueve fibras demasiado estrechas en una tarjeta se perdían al recortar alfa. Se cambió a cinco fibras más legibles en el mismo atlas, conservando geometría y tamaño de textura. Validar cobertura y mipmaps a la distancia de juego; no compensar un problema de cobertura duplicando tarjetas sin medir.

## Límites y siguiente comprobación

En una edición posterior se sustituyeron accesorios generados por una pieza independiente. Intersectar la superficie con un límite anatómico no rellena el volumen que falta debajo de un accesorio: puede conservar hondonadas cerradas y visualmente inadecuadas. La solución comprobada fue rellenar un sobre elipsoidal **solo en la región local de reconstrucción**, y después recortar el exceso, todo sobre el volumen unsigned antes de marching cubes. Se conservaron aparte las regiones delantera e inferior que no requerían cambios. El sobre es una decisión artística específica del recurso, no anatomía inferida automáticamente.

La nueva extracción produjo 272.724 triángulos, cero bordes abiertos/no manifold/degenerados, en 3,523 s CPU. El pico de working set del trabajador según el sistema operativo fue 240,02 MiB; el muestreo periódico registró menos y no debe sustituirlo como pico. Isovalor 0,501 evitó triángulos colineales por precisión float32 en esta frontera; registrar ese valor y revalidarlo en vez de asumir que 0,5 siempre da la misma integridad numérica. QuadriFlow y cierre de pequeños huecos terminaron en 36.874 triángulos de cuerpo, sin bordes abiertos ni aristas no manifold.

Un ensayo alternativo de Boolean exacto dejó siete uniones de más de dos caras. Remalla con signo y una llamada posterior de QuadriFlow no dieron una versión aceptada. Un operador puede devolver CANCELLED o advertir sin lanzar una excepción: comprobar FINISHED y el conteo final, además de la topología. Se rechazó una salida de más de 400k triángulos; no describirla como la retopología solicitada.

Para un accesorio independiente, colocar el pivote en su sujeción y ligarlo rígidamente a su hueso; sus detalles pueden agruparse por material y omitirse a distancia. No deformar la tela y la hebilla con el campo de pesos del torso. Reubicar articulaciones a partir de la malla actual: reutilizar coordenadas de otro personaje puede dejar las patas fuera del skin esperado. Volver a exportar y reimportar después de cada cambio final.

Conservar original, superficie reparada, retopología y material por separado. No llamar producción a una retopología automática solo porque esté cerrada: comprobar poses, pesos, UV, morphs, exportación/reimportación y finalmente motor/dispositivo. Mantener el detalle que aporta a la cámara elegida, crear LOD por coste real y no forzar uso de VRAM sin necesidad.
