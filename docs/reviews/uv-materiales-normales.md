# UV longitudinales, materiales compartidos y normales verificables

Guía basada en una revisión medida de autoría e integración. Incluye sólo observaciones agregadas y utilidades originales; no distribuye modelos, geometría exportada, imágenes, paletas o código de terceros.

## Orientar la veta por pieza y medir densidad

Una textura de madera plana puede ser adecuada y aun así verse incorrecta por UV: un cuadrado completo aplicado a cada cara de un marco estira la veta y la cruza en los elementos horizontales. Orientar un eje de UV a lo largo del eje longitudinal de cada listón, rotándolo en piezas perpendiculares. Para un swatch de P píxeles que representa una longitud virtual S, densidad propuesta=P/S; el tramo UV de una pieza de longitud L es L/S. Declarar esa longitud como elección artística, no dimensión física de una imagen generada.

Usar distancia sobre el perímetro de la sección para el eje transversal puede evitar UV degeneradas en biseles estrechos. Dar UV plana independiente a tapas. Comprobar el jacobiano de UV sobre los triángulos realmente exportados: la derivada de posición respecto al eje de veta debe ser longitudinal y la densidad debe mantenerse donde se espera. Mantener márgenes/crops dentro de 0..1 si el recurso no tiene continuidad de borde validada. Compartir imagen no exige repetir UV fuera de rango ni afirmar seamless. Evaluar mips/cámara normal, juntas y color antes de añadir normal map.

Si el renderer conserva una escala no uniforme, construir vértices en su espacio local no basta: comprobar que la normal final bajo la inversa transpuesta coincide con la normal geométrica de la cara en espacio métrico. No cambiar transformaciones que también sean referencia de desgaste, clic o apoyo sólo por simplificar el exportador. Verificar bounds y área libre sobre los mismos triángulos consumidos por motor, no una segunda fórmula que simplemente repita la intención.

## Separar mapa, paleta y desgaste

Localizar el último responsable de materiales después del arranque. Un constructor puede cargar un mapa que otro pase cambia después. Clonar únicamente el material de la superficie revisada, conservando identidad/paleta esperadas por el juego y una marca explícita que el pase artístico respete. Modificar un sharedMaterial puede alterar muchos objetos ajenos. Reutilizar la misma textura importada evita duplicados innecesarios; no cambiar su importador global por una necesidad local sin revisar los otros consumidores.

La modulación neutra se multiplica por el color del material sin volver a hornear la paleta. Roughness permanece una decisión artística constante cuando sólo existe una imagen RGB: no deducir PBR medido de una muestra generada. Mantener el renderer y el registro de desgaste cuando sea viable; intercambiar malla/material no debe borrar el MaterialPropertyBlock de condición ni mover el ancla local. Preparar recursos antes de publicarlos y restaurar sólo referencias todavía propias al destruir. La verificación de desgaste e interacciones requiere estados sintéticos en motor; estas reglas por sí solas no la acreditan.

## No confundir una comparación demasiado estricta con corrupción

En un caso medido de **Blender 5.2.3**, el primer verificador no superó reapertura al exigir error absoluto por componente<2e-5. Hubo cuatro imágenes, pero eso NO convirtió el intento en PASS: el fallo y la fuente original se conservaron. Un diagnóstico posterior abrió el snapshot sin guardar/renderizar y midió todas las esquinas contra expectativa y cara geométrica. La expectativa se reconstruyó con el mismo float32 del autor, además de una referencia float64.

| Observación agregada del caso | Resultado |
| --- | ---: |
| Esquinas comparadas | 336 |
| Esquinas que incumplen el requisito antiguo 2e-5 | 30 |
| Máximo error de componente |7.8448014392e-5|
| Máximo ángulo esperado/actual |0.00449474013°|
| Máximo ángulo expectativa cruda/cara guardada |0.00068302771°|
| Máximo error de longitud respecto a 1 |5.96046448e-8|

El segundo diagnóstico recreó únicamente mallas temporales no enlazadas con las mismas coordenadas, UV, flag de suavizado y llamada nativa para normales custom. **Las 336 esquinas recién asignadas coincidieron exactamente por componentes con el snapshot**, antes de guardar; la diferencia de coordenadas fue 0. Se eliminaron temporales y los hashes de fuente no cambiaron. Esto acota la discrepancia a la asignación/reconstrucción nativa de normales custom en ese entorno, antes de serialización; no se observó corrupción durante guardado. No demuestra un formato interno de bits concreto, ni un bug general de Blender, ni un defecto visible de render.

La revisión siguiente del verificador combinó explícitamente componente<=1e-4 Y ángulo<=0.01°, error de longitud<=1e-6, coherencia normal/cara<=0.01° y expectativa cruda/cara<=0.001°. Los 336 datos medidos cabían en todos esos límites. La comparación de topología/orden, posiciones, UV y bytes empaquetados siguió estricta. Se guardaron máximos observados y contexto de versión. Estos límites son **del caso**, no valores universales ni permiso para ocultar normales giradas, invertidas, no unitarias o mal indexadas. Otro recurso/versión exige medir antes de escoger sus límites.

No normalizar en silencio los vectores antes de medir su error de longitud o componente: se ocultaría una anomalía de magnitud. Para ángulo, normalizar copias y usar atan2(norm(cross),dot), estable cerca de 0°/180°. Corresponder vértices/esquinas por topología demostrada; la mera igualdad de conteos no prueba identidad. Comparar también con geometría real permite detectar una expectativa errónea compartida por ambas listas.

## Alcance y herramienta pequeña

El [helper normal_metrics.py](../../examples/normal-metrics/normal_metrics.py) es una función original de biblioteca estándar para estadísticas conjuntas. El llamador prueba la correspondencia y aporta normales geométricas si las tiene; no hay tolerancias predeterminadas universales. Devuelve medidas aunque no se suministren límites, y entonces `passed=None`. No guarda, corrige, asigna o cuantiza normales; tampoco analiza archivos de un motor ni identifica representación interna. Las pruebas sintéticas cubren ángulos muy pequeños/antiparalelos, magnitud incorrecta aunque ángulo 0, límites conjuntos e inputs inválidos. No son una validación del recurso de origen.

La reapertura aprobada es integridad del editable y del contrato comprobado, no aprobación visual general. Render aislado, cámara normal, día/noche, material final, desgaste, clic, apoyos y Player compilado son evidencias distintas. No extrapolar respuesta individual de todos los materiales desde un diferencial agregado, ni prometer FPS/VRAM por conteos o duración de un render. Conservar tanto el primer fallo como la corrección y su fundamento medido.
