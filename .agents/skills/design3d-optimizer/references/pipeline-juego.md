# UV, colisiones, exportación y perfilado en juego

## UV y baking

Costuras en zonas poco visibles; controlar estiramiento y texel density. Añadir padding suficiente para mipmaps; comprobar que el atlas no mezcle islas al reducir resolución. Compartir atlas solo cuando beneficie materiales/memoria sin sacrificar el acabado requerido.

Normal maps, AO y otros bakes requieren low poly con UV adecuadas, high poly o fuente procedente, tangentes y cage/distancias comprobados. El detalle fino no cambia silueta. Un mapa generado matemáticamente no debe llamarse bake high-to-low si no se hizo esa transferencia.

Unity Built-in, URP y HDRP no tienen materiales idénticos. Verificar convenciones de normales y mapeo metallic/roughness/smoothness, no conectar canales por nombre sin comprobar shader. Compresión por plataforma y mipmaps habituales en superficies 3D; medir memoria residente y calidad.

## Colisiones y LOD

Preferir primitivas o proxies compuestos simples cuando representen la interacción. Revisar restricciones de MeshCollider y cuerpos dinámicos de la versión concreta. No hacer colliders de cada hoja o pelo sin una necesidad demostrada.

LOD debe ahorrar más de lo que cuesta en memoria, transición y mantenimiento. Reducir materiales/renderers además de triángulos cuando resulte útil. La transición puede dibujar dos niveles temporalmente: medirla también. No unir todo un escenario y perder culling por ahorrar objetos.

## Prueba mínima de Blender a Unity

Probar un recurso y un par de clips antes de exportar lotes. FBX con selección/ejes horneados según pipeline; GLB requiere importador compatible en Unity, no asumir soporte de cualquier archivo por arrastrarlo a Assets. Comprobar escala, pivote, normales, texturas, rig y clips. Evitar dependencia del .blend y del Blender instalado de cada compañero para un build reproducible.

Los materiales rosas suelen requerir investigar shader/pipeline, pero no corregirlos a ciegas: revisar errores y dependencias. Escala 100x, root duplicado, tangentes o acciones mal exportadas necesitan pruebas concretas, no una receta universal de ejes.

## Medir rendimiento

Perfilar en build/dispositivo objetivo y escena representativa, no solo Editor. Registrar versión, calidad, cantidad de objetos, cámara y FPS objetivo. Profiler ayuda a localizar CPU/GPU/memoria; Frame Debugger a entender pases/dibujos, pero su captura no es un benchmark final de FPS.

Cambiar una variable por vez. Si el cuello es overdraw, quitar caras del tronco no lo arregla. Si es Animator/CPU, comprimir una textura puede no ayudar. Registrar picos de carga además de estado estable.

Usar Deep Profiling solo para investigar cuando aporte información: instrumentación añade coste. Los módulos de perfilado y el propio Editor también pueden cambiar medidas. Confirmar el efecto en condiciones comparables.

Fuente oficial de perfilado: [Unity 6000.6, plataforma objetivo](https://docs.unity.com/en-us/engine/6000.6/manual/analysis/profiler/profiling-applications/profiling-target-device). El curso Arm/Unity aportado está etiquetado Unity 2019.4: mantener conceptos y contrastar botones/APIs con la versión instalada.
