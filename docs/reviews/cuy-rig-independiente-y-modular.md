# Rig independiente y producción modular: lecciones de un personaje

Fecha de síntesis: 13 de noviembre de 2026. Evidencia anterior con Blender 5.2.3 LTS y Unity 6000.3.28f1. Estado: lecciones verificadas de un personaje reconstruido manualmente; la nueva generación StableGen completó cinco etapas de geometría. Se inspeccionó además un nuevo ejemplo estático modular, apto para exploración; rig, animación y aceptación de producción del nuevo recurso siguen pendientes.

Se publica conocimiento del procedimiento, no el personaje, sus fotos, archivos de otro juego o rutas del equipo. Los rasgos del ejemplo y sus presupuestos no se imponen a otros proyectos.

## Caso verificado y alcance

La prueba previa reconstruyó manualmente un personaje desde varias fotos, con una base editable, accesorios y rig. No fue una generación StableGen ni una reproducción exacta certificada de referencias que difieren entre sí. Se revisaron frente, tres cuartos, perfil y espalda antes de avanzar con la animación.

| Medida o prueba del caso manual | Resultado observado |
| --- | --- |
| Geometría exportada | 13.343 triángulos; 9.763 vértices GLB |
| Rig | 31 huesos deformantes exportados; 33 en editor, incluidos dos controles IK no deformantes |
| Materiales y primitivas | Tres materiales; cinco primitivas GLB |
| Imágenes | Dos atlas compartidos de 1024 × 1024 |
| Pesos | Máximo tres influencias; normalización y ausencia de vértices ligados sin peso comprobadas |
| Animaciones | Seis clips completos de tres segundos con cuerpo y cara sincronizados |
| Deformación muestreada | Cinco muestras por clip y diez estados de morphs por formato, en fuente y GLB reimportado; vértices finitos |
| Cierre con poses y mirada | 96 conjuntos de primer impacto en el GLB reimportado: cero globo visible, fallos o primeros impactos por caras traseras en lo muestreado |
| Orientación | 51 componentes topológicamente cerrados de la fuente, con volumen positivo y aristas coherentes; 18 regiones convexas de ojos/pies/dedos con 2.912 triángulos hacia fuera y cero hacia dentro |
| Pendiente conocido | 212 triángulos de área cero en neutral; no se probó que fueran inútiles en todas las deformaciones compatibles |

El visor independiente importó seis FBX y recorrió neutral más los seis estados en un Player nativo, con estado esperado y geometría finita. Se revisaron capturas y apoyos en muestras: las patas posteriores conservaron apoyo al elevar las anteriores. Eso no prueba contacto continuo, marcha natural o todos los extremos articulares. No se midieron FPS, memoria o batería en teléfonos.

La estructura del recurso y los bytes de sus atlas no son draw calls ni memoria GPU medidos. Una lista de importación que suma seis modelos tampoco es el coste de una instancia del prefab. Distinguir inventario completo, modelo canónico, escena en ejecución y dispositivo objetivo.

## Fallos que cambiaron el procedimiento

### Un control lateral debe conservar la otra mitad

Un target de cierre heredó el desplazamiento del otro lado al consolidar piezas. El guiño derecho cerraba ambos ojos y el valor 0,5 bilateral resultaba asimétrico. Inicializar cada destino completo desde Basis, copiar solo su región y mantener el espacio/orden de vértices corrigió el problema. En Blender, `shape_key_add(..., from_mix=False)` ayuda a evitar heredar una mezcla, pero no sustituye comprobar los datos.

Medir desplazamiento cero en la región ajena, además de ver el render. Revisar por separado 0/0,5/1, cada lado y la combinación bilateral. Preservar grupos anatómicos permite diagnosticar sin separar de nuevo todas las mallas.

### Cerrar en neutral no demuestra cerrar con mirada

Una lámina frontal ocultaba bien el globo en neutral y lo dejaba asomar en oblicuo. Un primer ajuste de borde empeoró el frontal. Casquetes completos resolvieron el neutral, pero un segundo ensayo con poses y los extremos reales de mirada encontró pequeñas fugas. El margen del target cerrado se ajustó sin cambiar Basis ni ocultar, escalar o desplazar el globo para fingir el resultado. Las proporciones y ese margen son específicos del caso.

Se verificaron tres vistas y ocho situaciones —seis poses intermedias y dos extremos medidos de mirada—, ambos ojos y dos clases de muestras: vértices y centros de caras. Son 96 conjuntos, no 96 escenarios del juego. Clasificar el primer objeto alcanzado como párpado, cuerpo, globo visible o fallo: el cuerpo también puede ocultar legítimamente una parte del ojo. Distinguir caras traseras evita atribuir cobertura a una superficie que el destino descarta. Complementar el muestreo geométrico con renders, cierres parciales y mezclas; no anunciar cobertura universal por esos ángulos limitados.

Este ensayo exigía que el globo permaneciera presente. Otros estilos pueden usar retracción ocular deliberada, como la [prueba anterior de materiales](materiales-accesorios-y-exportacion.md); documentar esa decisión y su curva, sin presentarla como anatomía universal ni confundir ambos contratos.

### Doble cara puede ocultar un generador incorrecto

Renders de presentación y glTF a doble cara ocultaron anillos de elipsoides orientados hacia dentro. Un material Standard que descarta caras traseras reveló huecos en ojos y pies. Corregir solo las normales de sombreado o activar doble cara no repara el winding.

Para cada primitiva convexa, comprobar el signo del producto cruzado de las aristas con el radio desde su centro: debe apuntar hacia fuera en los triángulos no degenerados. No aplicar esa prueba radial a orejas cóncavas u otras formas arbitrarias. En componentes cerrados, combinar orientación opuesta de aristas compartidas y volumen firmado positivo. Una comprobación posterior encontró también dos hojas cerradas invertidas por reflexión, aunque el generador de elipsoides ya estuviera corregido.

Comprobar después de aplicar transformaciones, espejar y consolidar, antes del bake y después de exportar. Al corregir superficies, rehacer los atlas/normales afectados y observarlos con el material real. Las superficies abiertas se registran aparte; no se les atribuye orientación de sólido ni se rellenan indiscriminadamente.

## Clips completos, bind y destino

El rig separó huesos deformantes de controles de autoría. El horneado conservó la deformación de apoyos IK al exportar; tener 33 huesos en el editor no incumplía un objetivo de 32 exportados cuando solo 31 deformaban el recurso. El número no demuestra que los controles funcionen.

Agrupar cuerpo y cara bajo cada estado lógico al exportar. Se verificaron seis nombres y duraciones de tres segundos, canales de transformación y pesos que cambian realmente, más su reproducción en el destino. La pose neutral restauraba bind y morphs por defecto: no era una séptima animación inventada. Los controles del visor no creaban un sistema emocional de gameplay.

Conservar targets `POSITION` y, cuando el destino use esas deformaciones, `NORMAL`; en este caso ambos se exportaron y comprobaron. Revisar skin, bind, jerarquía, rutas y curvas tras reimportar. Un archivo que contiene animación no demuestra que el controller la vincule al esqueleto correcto. Una nueva exportación requiere evidencia del archivo final: comparar datos de clips y bind permite reutilizar pruebas idénticas, pero no transferir aprobación de sombreado si cambiaron winding, normales o texturas.

## Base y accesorios: petición modular actual

La nueva petición plantea una base generada con StableGen sin complementos, revisión de anatomía/silueta y después piezas independientes. La generación de geometría completó cinco etapas reales; su ensamblaje estático y separación de módulos se inspeccionaron después. No se acredita anatomía de producción, rig o animación del nuevo recurso. El ensayo manual anterior no prueba automáticamente esta ruta de IA.

Aplicar la secuencia de la habilidad: base sin accesorios → revisión y movimiento de base → complemento de cabeza → mochila u otra pieza, cada una con pivote/sujeción y versión propia. No recortar una mochila de una generación fusionada y asumir que debajo existe anatomía sana; tampoco esconder hondonadas con el accesorio o pelo. Una pieza laminar necesita espesor y tratamiento distinto de un torso volumétrico. La [reparación de superficies](reparacion-superficie-generada.md) documenta un caso donde esa distinción fue necesaria.

Pendiente para la nueva entrega: aceptar la base visible sin accesorios, verificar cada pieza por separado y ensamblada, comprobar continuidad de UV/materiales, pesos/rig y clips, medir coste final y observar exportación en el destino. No copiar el asset del caso anterior para dar por terminada la petición.

## Nuevo RAW: cinco etapas completadas, modularidad pendiente

Se inspeccionaron los cinco registros de resultado del nuevo ensayo: todos indican finalización correcta. Configuración registrada: 512, doce pasos, semilla 13112026, INT8 ConvRot MPS y textura desactivada, mediante el grafo de StableGen y orquestación local de checkpoints.

| Etapa nueva | Tiempo registrado (s) |
| --- | ---: |
| Condicionamiento de imagen | 30,05 |
| Muestreo de estructura | 105,17 |
| Decodificación de estructura y preparación de forma | 15,02 |
| Muestreo de forma | 60,04 |
| Decodificación y exportación | 30,03 |
| Suma de registros | 240,31 |

Son tiempos del orquestador de este ensayo, no un benchmark de motor ni una medición normalizada comparable con otros equipos. Los registros informan un máximo observado de swap del sistema de 6,91 GiB y mínimo de memoria disponible de 3,04 GiB; no atribuir esos contadores globales exclusivamente al proceso ni confundirlos con VRAM. La aceptación de forma/materiales no se deduce de la finalización.

La inspección Python del GLB RAW nuevo registró **1.218.434 triángulos, 544.887 vértices, 21.161.284 bytes, una malla y un material**, sin imágenes, skin, morphs o animaciones. SHA-256: `12f0a0356a7887a2708224bae374fb7593e7ca5a0c96f529cb43ac97348510b4`. No se copió aquí el recurso ni la foto de entrada.

Es la salida geométrica, no una entrega lista para juego. Una malla no demuestra que la base anatómica esté libre de complementos fusionados; varios objetos tampoco demostrarían una separación correcta. Revisar cuerpo aislado, cada complemento y conjunto por vistas, sujeción/pivote, continuidad y defectos ocultos. Se observaron cinco vistas del RAW: incluye una plataforma de suelo generada y formas de adorno de cabeza/masa dorsal sin separación semántica aceptada. Las vistas no certifican por sí solas su conectividad topológica. No pasa todavía como base anatómica sin complementos. Retirar el suelo sin perder pies/dedos y reconstruir lo que falte bajo los accesorios antes de volver a montarlos; no ocultar el defecto con una nueva pieza. El inventario y la revisión estática posteriores se describen al final; no convierten el RAW en un recurso de juego sin su reparación. No reutilizar para él las métricas de 13.343 triángulos y seis clips del caso manual.

### Reparación actual: volumen local no equivale a una tapa

Se rechazó visualmente un candidato de limpieza que había perdido cara, orejas y patas y se leía como un óvalo. Un checkpoint posterior conservó las coordenadas anatómicas al retirar el suelo, pero mostró perforaciones/bandas: preservar la forma no demuestra cerrar la superficie.

En el siguiente candidato unsigned se observaron, desde tres cuartos y espalda, un agujero de coronilla y una tapa dorsal sobresaliente con una cavidad grande debajo. No se considera reparado. La lección es una condición de aceptación, no una técnica nueva ya aprobada: el patch local debe reconstruir un **volumen continuo** y su conexión con la base, no solo cubrir la proyección superior con una lámina.

El relleno de huecos binario no encierra por sí solo un interior que sigue comunicado con el exterior. Revisar los límites de la máscara en tres dimensiones, la unión con el volumen corporal y los cortes de prueba; proteger cara/patas/orejas frente a una sustitución global. Después comprobar la superficie extraída, sus bordes/componentes y las vistas, sin usar accesorios para ocultar el defecto. Los parámetros del ensayo unsigned anterior no garantizan la misma solución en esta nueva entrada. Un candidato posterior recuperó cara, orejas y pies y eliminó las grandes aberturas/tapa; ya no se reconocían complementos fusionados. Se permitió avanzar con accesorios separados en fase exploratoria, manteniendo una unión lateral escalonada y ondas como trabajo pendiente. Esa unión necesita un blend geométrico real antes de rig/aceptación final, no solo sombreado ni una mochila encima. Posteriormente se midió el cierre del cuerpo reducido y se inspeccionó el ensamblaje estático, con límites que se detallan abajo.

## StableGen: separar los equipos y las etapas

| Ensayo previo | Configuración y resultado propios | Lo que no demuestra |
| --- | --- | --- |
| Mac con M3 Pro y 18 GB de memoria unificada | StableGen 0.5.0/commit 68f2d165, ComfyUI 0.43.0 y PyTorch 2.9.0 MPS; INT8 ConvRot y cinco procesos/checkpoints produjeron geometría. Tiempo de fases 342,66 s, excluyendo arranque, descargas y preparación posterior. El intento BF16 se abortó tras alcanzar 14,78 GiB de swap. | No equivale a una GPU dedicada de 18 GB; no prueba el nuevo modelo modular, texturas/rig automáticos ni todos los flujos StableGen. |
| Windows con RTX 3050 Ti Laptop de 4 GB y 16 GB RAM | ComfyUI 0.45.0/PyTorch 2.7.1+cu126; muestreos en GPU y decodificación CPU, con procesos separados y perfiles de pesos por submodelo. Generación y color nativos TRELLIS.2 completados en ese ensayo. | No hereda los tiempos del Mac ni prueba que cualquier resolución/modelo quepa en 4 GB. El caso tiene mediciones y límites propios. |

El procedimiento y medidas del segundo caso siguen en [TRELLIS.2 en 4 GB](stablegen-trellis2-4gb.md). No mezclar sus picos de GPU/RAM, recuentos o resultados con el Mac ni sumar fases como memoria simultánea. Separar partes geométricas tampoco elimina el coste fijo de cargar pesos.

Los checkpoints espaciales deben conservar samples, coordenadas, contadores, resolución y marco; guardar solo samples no permite reanudar una forma sparse. Serializar tensores y datos simples de forma segura, guardar antes de terminar el proceso y validar cada salida. Adaptadores y versiones difieren: no declarar interoperabilidad de los checkpoints de ambos ensayos sin probarla. Una etapa de generación terminada no acredita retopología, UV, anatomía, rig o rendimiento móvil.

## Procedencia y mantenimiento

Síntesis propia de QA documentada del proyecto del usuario, consultada mediante informes/resúmenes saneados, reportes de importación/runtime y fixtures de prueba; no se traslada su personaje, fotos, nombres de gameplay ni configuraciones privadas. Las cifras identifican el alcance de esa evidencia, no un estándar para todos los juegos. Se publica esta redacción bajo la licencia de la biblioteca; no se atribuyen derechos sobre referencias o modelos de terceros.

Generalizaciones operativas en [rigging](../../.agents/skills/design3d-optimizer/references/rigging.md) y [exportación](../../.agents/skills/design3d-optimizer/references/exportacion.md). Actualizar el estado de la petición modular solo cuando existan artefacto, pruebas y observación de su propia versión.

## Resultado modular estático inspeccionado

Se ejecutaron `scripts/modular_report.py` en el Blend y GLB, y `scripts/glb_report.py` en el ensamblaje y los tres archivos de módulo. El nuevo ejemplo tiene **16.952 triángulos, 8.957 vértices exportados, 18 mallas/primitivas, 7 materiales y 421.076 bytes**, sin imágenes, skin, morphs o animaciones. La superficie del cuerpo derivada de IA aporta 14.000 triángulos; ojos/nariz, mochila y brote se construyeron manual/proceduralmente. El color corporal por vértices también es manual; no se atribuye a generación de texturas IA.

Los módulos finales son disjuntos y su unión coincide con los 18 nodos del ensamblaje: cuerpo 4 nodos/15.320 triángulos, mochila 12/1.584 y brote 2/48. El archivo de cuerpo incluye sus ojos y nariz complementarios. No se usa el número de objetos como prueba única: se revisó la base aislada antes y se observaron renders nuevos del GLB reimportado, frente/espalda, con materiales/color por vértices conservados y piezas reconocibles independientes.

En la fuente y una copia QA del reimportado con weld posicional 1e-7, el cuerpo reducido tuvo 0 bordes abiertos/no manifold, 7.002 vértices y volumen firmado positivo. El weld fue solo diagnóstico para no confundir splits de normales/color con agujeros; no modifica el asset. El conjunto cuenta 13 componentes cerrados correctamente orientados y cinco piezas tubulares con extremos abiertos (asa, tallo, correas y hebilla). No se certifica todo el ensamblaje como sólido cerrado ni como rig funcional.

La unión/superficie corporal y el acabado siguen siendo exploratorios. No hay nuevos seis clips, pesos, expresiones, contactos, UV/atlas de imagen o física interactiva comprobados. Tampoco medición de draw calls, FPS/memoria/batería en motor/teléfono. No trasladar aquí las cifras de 31 huesos, 51 componentes o 96 conjuntos de oclusión del caso manual anterior.

[Resumen saneado](../evidencias/modular/resumen-qa.json), [frente reimportado](../evidencias/modular/reimport-frente.png) y [espalda reimportada](../evidencias/modular/reimport-espalda.png). Validan la etapa estática modular, no todas las etapas del pipeline.
