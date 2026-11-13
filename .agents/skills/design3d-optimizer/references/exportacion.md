# Exportar y reimportar

Conservar .blend editable. Exportar selección explícita de personaje/rig/accesorios; excluir luces, cámaras, estudio y hebras de presentación.

GLB conserva PBR compatible, imágenes, skin y morphs/animaciones admitidas; no todos los nodos, drivers, constraints, física o curvas. FBX tiene límites/convenios distintos: elegir por motor y probar. Hornear cuando el comportamiento dependa de simulación o drivers.

Reimportar en escena limpia y revisar escala/orientación, bind pose, triángulos, materiales, imágenes, jerarquía, duración y expresiones. Comparar pose neutra, ojos cerrados, boca abierta, sonrisa y extremos de patas. Después probar en motor/dispositivo antes de declarar producción.

Costuras UV, normales y colores pueden dividir vértices exportados: contarlos además de los de autoría. Un objeto con ocho materiales suele tener varios grupos de dibujo; unir objetos no implica una sola draw call.

En pelo comprobar alphaMode/cutoff/doble cara y mipmaps. Un mapa procedural puede perderse: hornear o usar imágenes compatibles. Las utilidades incluidas inspeccionan estructura; no son validadores exhaustivos glTF ni benchmarks de juego.
