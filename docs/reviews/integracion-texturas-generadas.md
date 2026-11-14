# Integración de texturas generadas: autoridad visual y memoria

Revisión ampliada el 14 de noviembre de 2026. Método generalizado de un ensayo autorizado; no se redistribuyen sus recursos. [Ejemplo por etapas](../../examples/stablegen-sd15-staged/README.md) y [medidas resumidas](../evidencias/sd15-staged/resumen.json).

## Encontrar la autoridad visual

Seguir la construcción hasta después del arranque: quién crea la malla visible, oculta la anterior y modifica materiales. Un recurso importado correcto puede quedar reemplazado posteriormente. Ocultar renderers tampoco libera sus recursos. Compactar índices y vértices por grupo evita duplicaciones, pero exige medirlas; tres renderers no garantizan tres draws ni FPS.

Un pase artístico puede sustituir una textura de autor por otra procedural. Renombrar el material para esquivarlo también puede romper su pertenencia a la paleta. Separar ambas responsabilidades: conservar explícitamente el mapa, manteniendo recoloreado y desgaste. Comprobar arranque, reaplicación de estilo y cambios de estado, sin reasignar texturas cada fotograma.

Una prueba dirigida en Play del Editor conservó el mapa y la paleta en día y noche sobre un objeto de tres renderers y 2.860 triángulos; se comprobó una superficie de asiento a 0,62 m. No acredita todas las interacciones corporales, normales, respuesta PBR o rendimiento. La preparación falló primero por un identificador de metadatos mal formado, no por la importación de la malla; se corrigió conservando el original. Ese ensayo inicial no verificó normales; el seguimiento de Player descrito más abajo sí comprueba un efecto visible agregado, sin convertirlo en medición física del material.

## RAM y VRAM son presupuestos distintos

Equipo observado: Windows, RTX 3050 Ti de 4.096 MiB y 16 GB de RAM. Grafo común procedente de StableGen, adaptado a SD1.5 FP16: 512×512, lote 1, 20 pasos, Euler y CFG 5,5. Un nombre histórico del constructor no cambia la arquitectura real.

| Carga monolítica | Duración hasta parada | GPU total máxima observada | RAM disponible mínima |
| --- | ---: | ---: | ---: |
| Habitual | 19,78 s | 2.069 MiB | 1.759 MiB |
| Tras liberar RAM | 13,44 s | 400 MiB | 2.004 MiB |
| Dinámica respaldada por disco | 12,52 s | 400 MiB | 1.292 MiB |

Los tres intentos cruzaron la guardia de RAM y no produjeron imagen completa. Se conservaron umbrales de 2 GiB disponibles y 3.600 MiB de GPU total. El monitor muestrea cada 0,75 s más consultas: puede perder picos y reaccionar tarde. GPU total incluye otros procesos; las guardias no son límites físicos estrictos.

## Separar componentes y comprobar cada etapa

La partición por streaming verificó byte a byte 1.145 tensores F16: 197 de texto, 686 de difusión, 248 de VAE y 14 auxiliares preservados. No hubo entrenamiento ni cuantización; el original quedó intacto. Cada proceso cargó sólo su componente. Condicionamientos y latente se intercambiaron mediante safetensors CPU con estructura tipada, límites y recibos SHA, sin pickle. Se conservó el marcador nativo de escala del latente.

| Etapa | Tiempo del monitor | GPU total máxima | RAM disponible mínima | Resultado |
| --- | ---: | ---: | ---: | --- |
| Texto en GPU | 15,703 s | 722 MiB | 4.264.177.664 B | Ejecución correcta |
| Muestreo en GPU | 18,516 s | 2.259 MiB | 3.949.715.456 B | Latente guardado |
| VAE CPU, bloques 128/solape 32 | 60,329 s | 314 MiB | 4.379.430.912 B | Ejecución correcta; imagen rechazada |
| VAE CPU completo | 19,000 s | 314 MiB | 3.876.208.640 B | Primera textura aceptable |

El decode por bloques produjo discontinuidades visibles. Se decodificó **el mismo latente** completo, sin repetir muestreo ni cambiar semilla: desaparecieron los artefactos de mosaico observados. La comparación aísla el decode, sin garantizar identidad entre dispositivos o versiones.

Los primeros indicadores de cierre fueron falsos porque el lanzador no esperaba a su hijo. La auditoría posterior confirmó todos los procesos propios cerrados; se preservaron esos indicadores y se corrigió la espera. No se repitió inferencia para corregir el informe.

## Compatibilidad y alcance

El aviso específico de proyección de texto ausente se contrastó con el guardado SD1.5 y `return_projected_pooled=False`: no justificaba inventar pesos. Revisar cualquier otro aviso individualmente; conservar esta explicación junto al [código de referencia](https://github.com/Comfy-Org/ComfyUI/blob/c1eece62cbf1805d4f64286d7f5592e6a215e6ba/comfy/sd1_clip.py).

Son resultados locales, no garantía para cualquier GPU de 4 GB, panel completo StableGen, SDXL, multivista o juego final. Evaluar también continuidad, paleta, escala, luz y coste en motor. Los pesos SD1.5 conservan CreativeML OpenRAIL-M; [StableGen](https://github.com/sakalond/StableGen) conserva GPL-3.0 y las utilidades originales de esta biblioteca MIT, sin relicenciar dependencias ni pesos.

## Comprobar el editable y la superficie exportada

Al transformar código, JSON o identificadores con acentos, declarar UTF-8 tanto al leer como al escribir. Un cambio silencioso de codificación puede romper una comparación de nombres aunque el código compile. Separar ese fallo de observación de un defecto real del recurso.

Si la procedencia guarda hashes de scripts, fijar también sus finales de línea con reglas `eol=lf` en las rutas de autoría. Evitar volver a traducir CRLF ya decodificado al escribir en Windows; usar una escritura UTF-8 con LF explícito. Conservar hashes de las entradas congeladas y distinguirlos de la copia normalizada entregada. Verificar equivalencia de código y repetir la reproducción desde esa copia: una coincidencia previa no acredita un archivo modificado después.

En Blender por línea de comandos, un error del script Python puede dejar un código de salida cero. Usar `--python-exit-code 9`, exigir un informe explícito de la última comprobación y conservar el primer fallo. Una guardia de memoria aprobada acredita ese proceso, no todas las verificaciones del recurso.

Al reabrir un archivo, comparar las rutas relativas de imágenes después de resolverlas con `bpy.path.abspath` y normalizar separadores y mayúsculas del sistema. Seguir exigiendo el marcador relativo de Blender, permanencia dentro de la carpeta entregada, igualdad de bytes y empaquetado. No convertir una ruta absoluta en aceptable sólo porque la imagen esté empaquetada.

Una costura colocada sobre una curva analítica puede atravesar la versión triangulada de esa superficie. Comparar sus centros con la misma fórmula no detecta ese defecto. Proyectar el recorrido sobre los triángulos exportados, conservar los cruces donde cambia la pendiente y medir la piel del tubo, también entre anillos. La separación debe ser suficiente sin producir un hilo flotante. Revisar después la imagen en motor: excluir intersecciones no garantiza un ribete discreto ni elimina alias.

Las capturas cercanas deben encuadrar el recurso sin cortar al personaje. Una copia de presentación con las mismas mallas y materiales puede servir para ese diagnóstico, pero debe etiquetarse como modelo aislado. Mantener aparte la cámara normal de juego y las pruebas de interacción; un acercamiento aislado no prueba apoyos corporales.

## Normales artísticas y autoridad final de sombras

El [ejemplo CPU de mapas](../../examples/surface-texture-maps/README.md) genera modulación neutra y normales tangentes aproximadas a partir de luminancia. No recupera PBR físico, geometría medida, desplazamiento en milímetros ni roughness real: conserva una constante artística. La paleta se aplica como multiplicador separado; no hornearla de nuevo en el mapa. No afirmar continuidad de bordes ni tileado seamless sin comprobarlos.

Importar la normal RGB como `TextureImporterType.NormalMap`, desactivar conversión desde altura y tratarla como datos, sin sRGB. Comenzar con verde +V sin invertir y comprobar un relieve asimétrico en la base tangente real. Recalcular tangentes tras fijar vértices, normales, UV y triángulos, únicamente donde se use normal; rechazar UV degeneradas en esas superficies. El RGB PNG original y la representación importada de plataforma no son intercambiables sin verificar su empaquetado.

Activar `_NORMALMAP` en ejecución no demuestra que su variante exista en el Player: incluir una referencia serializada a un material compatible con esa keyword y verificar la compilación real. Una referencia retenida es preparación, no prueba final contra stripping. Una superficie sin normal debe mantenerla desactivada.

Seguir también quién decide las sombras al final del arranque. Desactivar sombras en el constructor puede ser sobrescrito por un pase de estilo posterior. Para ribetes muy finos, una política explícita del material puede indicar no proyectar sombra; el último configurador debe respetarla, manteniendo recepción de sombras si procede. No desactivar sombras de todo el objeto por un defecto de microdetalle. Validar después de todos los pases, no sólo en una copia que inventa otro shadow mode.

## Comprobación ON/OFF/ON en Player compilado

En el mismo fotograma y con cámara, luz, geometría, exposición y destino 512×512 idénticos, capturar normal ON, OFF y ON de nuevo. Restaurar keywords incluso ante error. Exigir repetición ON idéntica (`repeatNoise=0`) y una diferencia ON/OFF suficiente previamente fijada; ruido temporal o cambios de encuadre invalidan el aislamiento. Una copia aislada debe preservar las transformaciones relativas, materiales y shadow modes reales. Validar shader soportado, mapas presentes y tangentes; usar perfil sintético nuevo sin IA y salida nueva sin sobrescritura. Garantizar cierre con código de fallo incluso si no puede escribirse el informe.

Un Player Windows Direct3D11 en RTX 3050 Ti comprobó cuatro mapas 512, dos materiales con normales y cero errores. La macro de tejido tuvo 171.292 píxeles cambiados y repetición exacta. Esto demuestra efecto visible agregado de la variante en ese encuadre; no demuestra respuesta individual de ambos materiales, FPS, apoyos corporales, autonomía o conexión de un modelo de lenguaje. [Resumen saneado](../evidencias/surface-texture-player/resumen.json).

Dos builds previos se detuvieron por RAM. Un tercero compiló con Editor sin gráficos en 36,344 s, RAM disponible mínima 2.469.875.712 B y GPU total observada 314 MiB. Esto no es render sin GPU del juego: el Player posterior sí usó gráficos activos, duró 5,937 s, tuvo RAM mínima 5.803.442.176 B y GPU total observada 349 MiB. Según la [documentación primaria de Unity 6000.6](https://docs.unity.com/en-us/engine/6000.6/manual/unity-editor/command-line-arguments/editor), `-nographics` evita inicializar el dispositivo gráfico del Editor y no permite hornear GI que necesite GPU. Usarlo sólo donde corresponda; nunca como evidencia de imagen renderizada.

El Profiler devolvió cero para texturas en ese Player sin Development Build. Es una lectura no válida para cuantificar residencia, no cero VRAM. Las cifras de GPU total incluyen otros procesos y el monitor puede omitir picos entre muestras. Separar estimaciones de almacenamiento, lecturas válidas de recursos y observaciones globales del adaptador.

## Aceptar la muestra antes de derivar mapas

Una inferencia correcta puede producir un material inadecuado. En dos ensayos locales, pedir plástico ABS mate mediante el grafo común SD1.5 de StableGen produjo imágenes válidas, pero ninguna servía como muestra plana para una carcasa pequeña:

| Ensayo | Lectura de la imagen | Decisión artística |
| --- | --- | --- |
| Primera petición | Trama direccional semejante a tejido, fibras aparentes y puntos de color. | Rechazar como plástico mate; no derivar albedo o normal. |
| Petición más explícita | Pieza perforada con huecos y sombras geométricas incorporadas. | Rechazar como swatch: trasladaría agujeros y sombreado de otra pieza al objeto. |

Los dos casos completaron texto, difusión GPU y decode VAE completo CPU en procesos sucesivos; se conservaron los resultados técnicos y los rechazos visuales. No se generaron mapas derivados ni se integraron esas imágenes. La revisión no debe aprobarlas por tener un PNG correcto o una guardia de recursos en verde.

El perfil observado fue SD1.5 FP16, 512×512, lote 1, 20 pasos Euler/normal, CFG 5,5 y semilla 131113, con los mismos pesos. ComfyUI 0.45.0, PyTorch 2.7.1+cu126 y una RTX 3050 Ti de 4.096 MiB. Las seis fases pasaron sus guardias; el máximo de GPU total observado fue 2.259 MiB. En difusión, la RAM disponible mínima fue 3.518.648.320 y 3.821.551.616 bytes, respectivamente. El monitor muestreaba cada 0,75 s más consultas, podía omitir picos y contaba otros procesos en GPU. Esto acredita esos ensayos, no todo StableGen, SDXL o cualquier equipo de 4 GB.

Antes de convertir una referencia, revisar material representado, escala de detalle, direccionalidad, continuidad y sombras incorporadas. Una carcasa pequeña puede leerse mejor con su silueta y un material mate sin mapa que con ruido ajeno a su función o estilo. Documentar esa ausencia deliberada junto al rechazo; no hace falta encadenar inferencias para justificar una textura en cada objeto.

Si ya existe una muestra de madera aceptada, considerar su reutilización antes de generar otra: revisar UV longitudinales, densidad, paleta, mips y resultado en motor. Compartir textura no exige compartir el material mutable; clonar el material del objeto evita alterar otros recursos. No cambiar un importador global para corregir un único consumidor sin revisar los demás.

Una referencia procedural con img2img y denoise bajo sería un experimento posterior: **no se ejecutó aquí ni se validó su memoria**. Una plantilla procedente de StableGen conserva su licencia GPL y no debe presentarse como utilidad original MIT. Esta lección no incorpora esa plantilla, imágenes, pesos, geometría o configuraciones de otro proyecto, ni atribuye a la generación de texturas la autoría de una malla manual.

## UV y normales al reutilizar una textura

La [guía de UV longitudinales, materiales compartidos y normales verificables](uv-materiales-normales.md) explica cómo conservar paleta y desgaste, medir densidad sobre los datos exportados y diagnosticar una discrepancia de normales antes de atribuirla al guardado. Incluye un helper original con cuatro pruebas sintéticas; sus límites medidos son específicos del caso y no sustituyen revisión visual o pruebas en motor.

## Mallas compartidas y evidencia de contacto

La [guía de mallas compartidas y evidencia corporal](mallas-compartidas-evidencia-corporal.md) distingue recursos únicos de sumas por renderer, restauración, captura y autoridad de transformaciones. Incluye límites de las contrapruebas geométricas y del alcance: completar una secuencia dirigida no aprueba piel, postura o contactos.
