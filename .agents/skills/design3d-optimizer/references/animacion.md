# Acciones, animación y colaboración

## Definir lo necesario

Separar acciones requeridas de catálogo deseable: idle, locomoción, salto/aterrizaje, ataque, reacción, interacción o muerte solo cuando el juego las necesite. Para escenarios: apertura, mecanismos, destrucción o crecimiento; para VFX: emisión, evolución y salida.

Registrar nombres, FPS, duración, looping, Root Motion o movimiento por controlador, puntos de contacto y eventos de gameplay. El evento de impacto/cancelación debe controlarse de forma coherente con la lógica; no depender de una imagen de la animación.

## En Blender

Una acción reutilizable por clip cuando corresponda. Organizar Action Editor/NLA y revisar slots de acciones en versiones recientes. Hornear constraints/IK cuando el formato no los transporte. No mezclar todos los movimientos definitivos en una sola demostración si el motor necesita clips separados.

Walk/run: continuidad de contactos y velocidades; revisar foot sliding con el controlador real. Primer/último frame visualmente iguales no garantizan velocidad continua. Un movimiento sinusoidal de patas muestra el rig, pero no equivale a locomoción pulida con apoyo y traslado de peso.

Cara: probar combinaciones de visemas, sonrisa y parpadeo; respetar topología de shape keys. No dar por reproducido un acting completo con tres morphs. En accesorios, probar motion entre extremos y no solo una captura.

## Unity, cuando sea el motor elegido

Elegir Generic/Humanoid por anatomía y compatibilidad, no por preferencia universal. Para un cuy, no asumir que el avatar humanoide representa correctamente sus patas. Documentar versión y render pipeline; no instalar paquetes @latest sin fijar compatibilidad.

Animator Controller organiza estados/transiciones. Un Blend Tree 1D puede interpolar locomoción por velocidad; 2D puede representar dirección. Calibrar parámetros con velocidad del controlador y probar inicio/parada, cambios de dirección, interrupciones y reentrada.

Decidir Root Motion vs controlador y probar que no haya movimiento doble. IK de pies/manos y Animation Rigging son sistemas de runtime con costes/orden de evaluación; los constraints de Blender no se convierten automáticamente en ellos.

## Optimización y colaboración

Medir Animator, skin, blends y memoria en escena representativa. Reducir muestreo, complejidad y secundarios fuera de cámara solo si el comportamiento de gameplay lo permite. No apagar a ciegas lógica que afecte contactos o eventos.

El animador y programador acuerdan pivotes, nombres, clips, root, parámetros, sockets y eventos. Conservar fuente y exportación; no editar la misma escena simultáneamente. Registrar cambios que invaliden pesos o clips antes de que otra persona los use.

## Evidencia actual del ejemplo

El cuy incluye una demostración de 72 frames: patas, cabeza, morphs y resortes secundarios. Se comprueban en Blender y reimportación GLB. No hay Animator/Blend Trees, colisión continua, clips de gameplay pulidos ni física interactiva Unity validados. Su clip no se presenta como ciclo de caminar listo para producción.

Las guías originales aportadas por el usuario están catalogadas en la [biblioteca del repositorio](https://github.com/extremedan360/Design3dOptimizer/tree/main/docs/library); usar versiones correspondientes al proyecto.
