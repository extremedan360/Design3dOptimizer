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
