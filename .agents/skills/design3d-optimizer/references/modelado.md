# Forma, sombreado y materiales

Diseñar desde la cámara prevista. Silueta, proporciones, ojos y masas grandes suelen aportar más que microdetalle. Evaluar frente, perfil y tres cuartos; no quitar detalle solo porque desaparezca en una miniatura.

Flujo: bloquear cuerpo/cabeza/patas → ajustar referencia → materiales → pelaje/accesorios → poses y expresiones → exportación. Las piezas separadas facilitan cambios y pesos rígidos, pero sus intersecciones no equivalen a una malla continua para deformación orgánica.

Smooth shading interpola normales sin redondear el contorno. Añadir segmentos donde aún se vean facetas. Smooth Vertices mueve posiciones: puede encoger la forma y no crea topología anatómica automáticamente. Mantener subdivisión acotada y revisar geometría evaluada, no solo la malla base.

Usar geometría para contorno/articulaciones; normales/rugosidad para detalle que no necesite volumen real. Normal map cambia respuesta a luz, no posición. Colores por vértice ahorran atlas pero su resolución depende de la malla.

Los nodos procedurales no se transfieren íntegros a GLB/FBX. Hornear o sustituir por imágenes/nodos compatibles. Guardar cámara, resolución, muestras y representación al comparar; si cambian varias condiciones no atribuir todo a una optimización.

Accesorios con igual modelo de sombreado y distinto color pueden compartir material y usar colores por vértice. En el ejemplo: 13 materiales/15 grupos a 4/7, conservando 20.360 triángulos. Revisar el acabado al compartir propiedades; no atribuir FPS sin medir en motor.
