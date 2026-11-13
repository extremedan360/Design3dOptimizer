# Forma, sombreado y materiales

Diseñar desde la cámara prevista. Silueta, proporciones, ojos y masas grandes suelen aportar más que microdetalle. Evaluar frente, perfil y tres cuartos; no quitar detalle solo porque desaparezca en una miniatura.

Flujo de personajes: bloquear cuerpo/cabeza/patas → ajustar y revisar la base sin complementos → topología/materiales y pruebas de movimiento de la base → cada complemento independiente → pelaje integrado y poses combinadas → exportación. Las piezas separadas facilitan cambios y pesos rígidos, pero sus intersecciones no equivalen a una malla continua para deformación orgánica.

## Base primero, complementos después

Construir el personaje sin ropa ni accesorios y revisar frente, perfil, espalda y vista superior. Comprobar anatomía propia del ser: cantidad y colocación de miembros, cara, orejas y presencia o ausencia de cola visible. La referencia estilizada guía el diseño, pero un saliente generado no debe aceptarse automáticamente como parte anatómica. Corregirlo antes de vestir o equipar al personaje.

Guardar la base editable. Revisar articulaciones y poses necesarias antes de añadir elementos que tapen sus defectos. El pelaje superficial puede prepararse en la base, pero no sustituye una silueta sana; terminar su colocación después de conocer ropa y accesorios.

Añadir una pieza por etapa: primero un complemento pequeño, después ropa/equipamiento más complejo. Ejemplo de animal estilizado: animal base → brote/adorno de cabeza → mochila. Un adorno vegetal delgado conviene como pieza separada, con base fija y pivote en el tallo; no confiar en que la retopología global conserve su espesor.

## Ajuste funcional de ropa y equipamiento

Antes de detallar, definir cómo se sostiene, para qué sirve y cómo lo usa el personaje. En una mochila: posición de la carga, tamaño frente al cuerpo, correas o arnés, puntos de apoyo, apertura, bolsillos y alcance de las extremidades. En un cuadrúpedo del juego, diseñar la sujeción sobre su torso y dejar libres cuello y articulaciones; no pegar una mochila con disposición humana sin adaptar su uso. Lo fantástico puede ser estilizado, pero la sujeción y el movimiento deben ser legibles.

Probar primero un bloque simple sobre la base en reposo, caminar, girar y agacharse. Ajustar separación y escala para evitar flotación, penetración, deslizamiento o limitación involuntaria de las patas. Luego modelar solapas, costuras y herrajes; llevar grano de tela/cuero a texturas y normales cuando no afecte al contorno.

Mantener ropa, hoja y mochila editables e identificables. Unir piezas por material para exportar cuando convenga, conservando una copia de autoría. Asignar la mochila rígida a su hueso de sujeción; correas blandas y elementos colgantes pueden requerir pesos/guías propios. No deformar una hebilla rígida con los pesos del cuerpo.

El movimiento secundario debe responder a la carga y a los anclajes: oscilación corta, límites de giro, amortiguación y comprobación de contacto. Hornear una demostración no implementa colisiones ni física interactiva del motor. Revisar máscaras de pelo y márgenes de puntas después de colocar cada complemento.

Smooth shading interpola normales sin redondear el contorno. Añadir segmentos donde aún se vean facetas. Smooth Vertices mueve posiciones: puede encoger la forma y no crea topología anatómica automáticamente. Mantener subdivisión acotada y revisar geometría evaluada, no solo la malla base.

Usar geometría para contorno/articulaciones; normales/rugosidad para detalle que no necesite volumen real. Normal map cambia respuesta a luz, no posición. Colores por vértice ahorran atlas pero su resolución depende de la malla.

Los nodos procedurales no se transfieren íntegros a GLB/FBX. Hornear o sustituir por imágenes/nodos compatibles. Guardar cámara, resolución, muestras y representación al comparar; si cambian varias condiciones no atribuir todo a una optimización.

Accesorios con igual modelo de sombreado y distinto color pueden compartir material y usar colores por vértice. En el ejemplo: 13 materiales/15 grupos a 4/7, conservando 20.360 triángulos. Revisar el acabado al compartir propiedades; no atribuir FPS sin medir en motor.
