# Expresiones y pelaje: comprobación por etapas

Fecha: 2026-11-12. Prueba original con Blender 5.2.3 LTS; no incorpora imágenes ni modelos privados de referencia.

## Lecciones probadas

- Unir volúmenes y remallar antes de crear shape keys o pesos permite suavizar encuentros entre cabeza y mejillas. La remalla cambia la topología: revisar UV, colores y pesos después. No aplicarla a ojos, controles faciales o piezas que deban conservar identidad.
- Un párpado que interpola entre dos bordes puede atravesar el iris aunque ambos bordes parezcan correctos. En el ensayo, cubrir solo el globo dejó la pupila visible durante Blink=1. Proyectar también los anillos intermedios por delante de toda la envolvente ocular corrigió la cobertura; comprobar lateral, frontal, cierre y expresiones combinadas. Una cobertura correcta todavía puede tener aspecto de placa: requiere ajuste artístico.
- Al consolidar mallas faciales, conservar un destino independiente por objeto y control (por ejemplo, lado__Blink). Fusionar controles homónimos pierde asimetría. Transformar base y destinos al mismo espacio, copiar atributos y muestrear las curvas originales antes de retirar sus objetos.
- Si se inclina la cara usando un padre, el volumen continuo y el pelo deben acompañarla. Usar un rig coherente o deformación ponderada de presentación; reiniciar desde posiciones de reposo para evitar acumulación entre presets.
- Separar render con curvas de pelo y malla con tarjetas. El buen resultado del primero no verifica el acabado ni el coste del segundo. Inspeccionar tarjetas con el material y alpha exportados: raíces visibles y manchas requieren revisión del peinado, densidad y atlas.

## Evidencia y límites

En una prueba local, la reimportación GLB conservó 23 huesos, 29 destinos faciales independientes y sumas de pesos normalizadas. Se inspeccionaron cinco estados renderizados, incluidos cierre de ojos y apertura de boca. Un GLB agrupado en tres mallas tuvo siete primitivas y cuatro materiales: contar objetos no equivale a medir llamadas de dibujo.

Los picos observados se obtuvieron por muestreo periódico del proceso Blender y de toda la GPU, por lo que pueden perder máximos y la GPU incluye otras aplicaciones. No equivalen a VRAM ni FPS del motor. Tampoco una animación de resortes horneada demuestra física interactiva.

Las cifras de triángulos, huesos y resolución escritas en una lámina de referencia son objetivos ilustrativos hasta medir el recurso real. Validar silueta a distancia de juego y diseñar LOD a partir de ese resultado; no atribuir al modelo LOD que aún no existen.

Estado: comportamiento de exportación y cobertura probado en este ensayo; aceptación visual, perfiles del motor, colisiones y rendimiento en dispositivo pendientes. Procedencia: experimentación y documentación originales, MIT.

## Segunda iteración: forma y presupuesto

Una dirección artística de mayor calidad no implica minimizar todos los polígonos. Se probaron orejas cóncavas con espesor y borde plegado, más segmentos en los contornos y dedos geométricos. Conservar el principal detallado y reducir a distancia permite separar acabado cercano de coste por muchos personajes. No decimar la cara con shape keys sin transferir los destinos.

Para una variante estilizada del parpadeo se probó retraer ligeramente el conjunto ocular sin aplastarlo mientras la piel de cierre se aproxima a la superficie de la cabeza. Eso reduce la placa abultada; no es una descripción anatómica universal. La retracción debe animarse junto al párpado y comprobarse después de consolidar y exportar, incluyendo cierres parciales.

Las tarjetas requieren que coincidan el orden de sus vértices, la normal geométrica y las normales transferidas. Un material a doble cara puede invertir el sombreado del reverso aunque las normales personalizadas parezcan apuntar hacia fuera. Comprobar el producto escalar con la normal de la superficie y una vista exportada; no intentar tapar un error de orientación aumentando densidad.

Al decimar una malla con skin, colocar el modificador antes de Armature para trabajar sobre reposo; aplicarlo después puede incorporar una pose al resultado. Normalizar pesos y reimportar cada LOD. Exportar archivos con menos triángulos no crea automáticamente un sistema de selección de distancia en el motor.

## Carga de IA y memoria del sistema

En una prueba con 16 GB de RAM y 4 GB de VRAM, los monitores interrumpieron cargas de SDXL antes del muestreo: el problema apareció en RAM, incluso antes de ocupar la GPU. Se ensayaron almacenamiento FP16, conversión FP8 durante la carga y un checkpoint con UNet FP8 convertido previamente. No bastaron en ese entorno; no convertir esto en un mínimo universal para todos los equipos/versiones.

La conversión previa por tensor mediante lectura mapeada evitó cargar dos copias completas durante la conversión, pero no eliminó las asignaciones posteriores del cargador de inferencia. Registrar ambos pasos por separado. Low VRAM no significa bajo consumo de RAM; llenar una cuota de GPU tampoco mejora por sí solo una imagen.

Probar un modelo menor en una tarea acotada, sin ejecutar Cycles simultáneamente. Separar registro del complemento, conexión del servidor, generación, proyección, horneado y exportación: pasar una de esas pruebas no demuestra las restantes. Las mediciones son observaciones periódicas y el monitor puede reaccionar después de un pico corto.

Después se comprobó generación acotada con SD1.5 FP16 mediante el constructor de nodos txt2img comunes de StableGen, adaptando el checkpoint y la resolución por subclase sin modificar su fuente. No demuestra compatibilidad del flujo SDXL ControlNet ni generación 3D. A 768 × 768, 20 pasos: 48,31 s, GPU total máxima observada 3.065 MiB, RSS máximo de un proceso servidor 4.948,3 MiB y RAM disponible mínima 4.255,7 MiB. Son medidas de este ensayo, no requisitos ni FPS del juego.

La primera imagen incluyó un ojo pese a los negativos y fue rechazada. Una segunda petición centrada en una muestra de material evitó anatomía, pero conservó pequeños defectos de color. Para microdetalle se ensayó solo luminancia de contraste acotado multiplicada por los colores originales y horneada en un atlas UV de 1024². No llamar albedo físico a una imagen de difusión ni aplicar una textura defectuosa solo porque terminó la inferencia. Revisar el horneado y comprobar que su imagen está realmente en el GLB.
