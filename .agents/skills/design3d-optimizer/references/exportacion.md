# Exportar y reimportar

Conservar .blend editable. Exportar selección explícita de personaje/rig/accesorios; excluir luces, cámaras, estudio y hebras de presentación.

GLB conserva PBR compatible, imágenes, skin y morphs/animaciones admitidas; no todos los nodos, drivers, constraints, física o curvas. FBX tiene límites/convenios distintos: elegir por motor y probar. Hornear cuando el comportamiento dependa de simulación o drivers.

Reimportar en escena limpia y revisar escala/orientación, bind pose, triángulos, materiales, imágenes, jerarquía, duración y expresiones. Comparar pose neutra, ojos cerrados, boca abierta, sonrisa y extremos de patas. Después probar en motor/dispositivo antes de declarar producción.

Costuras UV, normales y colores pueden dividir vértices exportados: contarlos además de los de autoría. Un objeto con ocho materiales suele tener varios grupos de dibujo; unir objetos no implica una sola draw call.

En pelo comprobar alphaMode/cutoff/doble cara y mipmaps. Un mapa procedural puede perderse: hornear o usar imágenes compatibles. Las utilidades incluidas inspeccionan estructura; no son validadores exhaustivos glTF ni benchmarks de juego.

## Winding, morphs y pruebas del archivo final

Comprobar orientación después de aplicar transformaciones, espejar o consolidar y antes del bake. En primitivas convexas, el producto cruzado de aristas debe apuntar hacia fuera respecto a un punto interior conocido, no a un origen de objeto supuesto; esa prueba no sirve para una cavidad cóncava arbitraria. Para componentes cerrados, verificar aristas compartidas orientadas en sentidos opuestos y volumen firmado positivo. Registrar superficies abiertas aparte. Normales de sombreado finitas o un material doble cara pueden ocultar un winding que FBX/Standard descarta. Tras corregirlo, revisar también el bake, normales y material reimportado.

Inspeccionar targets `POSITION` y `NORMAL` cuando el destino use normales deformadas, índices/orden de vértices, skin/bind, imágenes y canales reales de animación. Comprobar nombres, duración y cambio efectivo de cuerpo/cara por clip, además de la asignación del controller en el destino. Restaurar neutral no requiere inventar un clip adicional. No atribuir eventos de gameplay a una exportación si no se conservaron o implementaron.

Separar inventario de varios archivos, instancia canónica y escena runtime. Primitivas/materiales o bytes de PNG no son draw calls, memoria residente o FPS medidos. Una cara de área cero en neutral puede abrirse con morphs o pesos: no eliminarla sin revisar los estados compatibles. Comparar hashes/datos puede transferir una prueba de clips idénticos; cambios de normales, winding o atlas exigen su propia revisión visual. Ver [evidencia del caso y límites del ejemplo modular](../../../../docs/reviews/cuy-rig-independiente-y-modular.md).
