# Mallas compartidas, restauración y evidencia corporal

Lección general de un caso medido en Unity 6 sobre Windows, revisado el 14 de noviembre de 2026. Distingue inspección, ejecución dirigida, contraprueba geométrica y propuesta de animación. No distribuye recursos, poses, coordenadas, paletas, capturas o datos del proyecto de origen.

## Contar recursos sin confundir denominadores

Registrar por separado mallas únicas, triángulos/vértices en esas mallas, sumas por renderer y sumas visibles/ocultas. Cuatro renderers pueden compartir una sola malla: sumar sus triángulos describe las instancias, no cuatro asignaciones geométricas independientes. Un editable de cinco piezas tampoco implica cinco mallas runtime únicas.

Deduplicar sólo después de validar cada descriptor completo. Para compartir patas iguales, comprobar secuencialmente vértices, normales, UV e índices; posiciones y escalas se validan aparte. No usar nombre, conteo o parecido visual como identidad. Una pieza válida distinta debe conservar su malla propia. Compartir textura no exige compartir un material mutable.

Menos triángulos únicos puede acompañarse de más vértices únicos. La geometría anterior puede seguir referenciada para restauración o por otros consumidores: bajar una suma no demuestra que desaparezca de memoria. Ni estas cuentas ni menos renderers acreditan FPS, draw calls efectivos o VRAM liberada.

## Propiedad de aliases y restauración por etapas

Preparar recursos antes de publicar referencias. Guardar las preimágenes exactas de cada consumidor; ante error, restaurar primero las referencias que todavía pertenecen al componente. No sobrescribir una referencia que otro sistema ya sustituyó.

Antes de cualquier Destroy diferido, reunir las mallas propias en un conjunto tipado de identidades únicas; destruir cada una una sola vez. No liberar por renderer una malla compartida ni usar el cambio de “null” de Unity tras destruir como mecanismo de deduplicación. Material original, textura prestada y recursos compartidos ajenos permanecen fuera de esa propiedad.

Separar rechazo de esquema, fallo tardío de descriptor y destrucción normal. Un fallo después de preparar mallas pero antes de crear material sólo prueba limpieza de esas mallas: conservar explícitamente que no ejercitó liberación del material. Destruir el componente y esperar varios frames aporta otra evidencia; no certifica todos los fallos posteriores a asignaciones, heap o GPU.

La preimagen guardada durante Awake puede ser un Cube; Start o un pase artístico posterior puede convertirla en bevel compartido. Un teardown correcto puede restaurar primero Cube y, tras reaplicar estilo, volver al bevel. Validar ambas etapas, identidades, flags y registros; no declarar un fallo sólo porque las mallas de esas dos etapas sean distintas.

## El informe también necesita presupuesto

Un ensayo produjo imágenes y ejecutó su secuencia, pero falló al serializar JSON pretty por superar un límite de 4 MiB: terminó con error y sin resultado. Conservar ese fallo; renderizar capturas no lo convierte en PASS.

La repetición mantuvo secuencia, gates y límites, usando JSON compacto y una sola ubicación para muestras antes duplicadas. Cerró con un resultado de aproximadamente 1,33 MB. Esto corrige almacenamiento de observación, no la animación. Verificar al leer que siguen presentes grupos, muestras, distancias negativas y metadatos; no recortar evidencia adversa para caber ni elevar silenciosamente el límite. Cierre de procesos, guardias y aprobación artística siguen siendo comprobaciones separadas.

## Aislar la contribución geométrica

Dos ejecuciones corporales pueden capturar fases ligeramente diferentes. Para comparar muestreos de distinta densidad, comenzar por índices comunes y publicar aparte los puntos añadidos. Un mínimo menor al aumentar cobertura no demuestra mejora de pose. Un indicador de grupos accesibles completos tampoco prueba toda la piel, triángulos o trayectoria.

Una contraprueba más estricta conserva la MISMA pose y los mismos puntos world de piel horneada. Obtiene las dos mallas nativas reales, verifica sus identidades y matrices, y aplica exactamente la misma transformación a ambas. La superficie nueva debe reproducir los signos y distancias capturados dentro de una tolerancia numérica previamente justificada. No reconstruir aproximadamente la superficie antigua con otra fórmula.

En un caso, un punto pasó a intersección local de aproximadamente 0,8 mm y una muestra de manga pasó de unos 13,8 a 16,1 mm de penetración al comparar superficies. La contraprueba separa contribución de geometría y defecto corporal heredado; no observa una ejecución corporal antigua que nunca se capturó. Paridad de rayos y distancias de muestras no son colisión volumétrica o temporal exhaustiva. No mover mobiliario ni ocultar piel para aprobar.

## Base angular inmutable y pivote con traslación viva

Una entrada puede tener orientación ya estable mientras su soporte visual aún converge o mantiene movimiento permitido. Congelar también la posición del pivote hace que el preflight calcule hombros desde una referencia que el cuerpo real ya dejó atrás. En un ensayo cerrado, una reserva izquierda quedó retenida en 9,57 mm frente al gate de 10 mm; nunca se aplicó la pose y terminó por timeout. No fue prueba de contacto ni motivo para bajar el margen.

Separar dos contratos: base angular y offsets originales inmutables, para no acumular la inclinación del propio modificador; origen de traslación vivo, tomado de un pivote upstream que el modificador no traslada. Su rotación propia no cambia la posición de ese pivote. No recapturar toda la pose actual, que puede contener la corrección anterior. Si cambian jerarquía, orientación upstream o el soporte más allá de los límites admitidos, invalidar la referencia en lugar de asumir que basta trasladarla.

La reconstrucción CPU conservó orientaciones, offsets, targets y gate, sustituyendo sólo el origen de traslación. Reprodujo primero el cálculo congelado y contrastó la traslación con hombros medidos. Los rechazos iniciales se conservaron; en la parte asentada, ambas reservas superaron el mismo umbral. Es una contraprueba matemática sobre capturas. Una ejecución nativa posterior avanzó y completó permanencias dirigidas y salidas, pero siguió fallando comprobaciones de piel. Se conserva como FAIL: el avance de secuencia no acredita aceptación corporal, postura, mirada o colisión continua.

Medir ambos brazos antes de combinar su aceptación. Un `izquierda && derecha` que ejecuta mediciones dentro del booleano puede dejar el diagnóstico derecho sin actualizar cuando falla la izquierda. Publicar frame, referencia capturada y viva, finitud, distancias y reservas de ambos; sólo después decidir. Mantener los gates originales para separar una corrección de referencia de un cambio de criterio destinado a pasar.

## Atribuir autoridad en la misma llamada

No comparar sólo snapshots finales de frames distintos para afirmar que un modificador trasladó un root visual. El soporte, suavizado y grounding pueden ser dueños legítimos de variaciones previas. Observar inmediatamente antes y después de la misma llamada, una vez terminado el filtro upstream: identidad, posiciones/escalas locales de huesos controlados y transforms que el modificador no posee. Las rotaciones permitidas pueden mover descendientes en world; no exigir invariancia de esas posiciones world por error.

Mantener aparte el contrato temporal del actor y sus apoyos. La invariancia del actor world root no equivale a congelar su root visual o todos los hips world entre frames. Registrar qué dueño y fase explican cada magnitud. No aumentar una tolerancia hasta que desaparezca el fallo: corregir primero la atribución. Guardar el frame fallido, pre/post y cada término antes del assert. Una excepción lanzada por el observador puede ser contada como error runtime por un listener; clasificar su origen sin ocultarla ni adjudicarla al motor o a inferencia no observada.

## Comparación numérica y preparación de evidencia

Un ángulo derivado de un cuaternión consigo mismo puede resultar pequeño pero no nulo si sus componentes float no tienen norma exactamente uno. Conservar componentes y norma crudas; comparar componentes y calcular el ángulo sobre copias normalizadas válidas. Considerar el signo equivalente de una rotación sólo en la comparación de orientación. No normalizar datos inválidos para hacerlos pasar ni interpretar un ángulo aislado como una escritura distinta del transform. Los límites siguen siendo medidos por caso.

Al derivar hashes desde código, declarar UTF-8 tanto en lectura como en escritura y explicitar la política de finales de línea. En el caso revisado, una lectura cp1252 produjo un pin incorrecto de un archivo UTF-8; no era una modificación de su lógica. Fijar primero los bytes de entrada, conservar el fallo y repetir la derivación con encoding correcto. Si se normaliza texto, registrar separadamente bytes originales, bytes entregados y equivalencia de código; no intercambiar esas identidades.

Validar también el esquema del manifiesto antes de cualquier proceso pesado: un campo de archivos puede ser diccionario ruta→hash o lista de registros. No asumir una forma heredada de otro paquete. Comprobar tipos, campos requeridos, unicidad de rutas y preimágenes antes de copiar o ejecutar. Un error de lectura de manifiesto, encoding o pin no debe convertirse en un falso fallo nativo ni justificar repetir innecesariamente inferencia o compilación.

## Alcance de brazos antes de prometer IK

Con hombro fijo y segmentos de longitudes a y b, la muñeca no supera a+b. Añadiendo el radio máximo r de toda la piel rígida de mano respecto de la muñeca, ningún punto supera a+b+r. Comparar ese límite externo con la distancia mínima del hombro a los triángulos reales del objetivo. Si la distancia lo excede, cambiar sólo ángulos no puede producir contacto; no confundirlo con fallo de un solver ni estirar huesos para ocultarlo.

Usar un máximo de piel, no su radio medio, y distancia a triángulos, no sólo al centro de un bounds. Quedar dentro de la esfera es condición necesaria, no suficiente: faltan orientación, límites articulares, ropa, torso, silla y trayectorias. Una manopla continua aporta soporte geométrico, no dedos anatómicos inventados.

Un grid de posturas sólo explora candidatos matemáticos. Sus rangos no son ergonomía o ROM aprobados; su función de coste no mide naturalidad. Cambiar hombros/torso exige revisar apoyo, alcance y colisiones en motor. La auditoría y una implementación aislada de IK seguían sin aprobación funcional al cerrar esta lección; no se presenta un sistema de contacto ya terminado.

Conservar evidencias de fallo y separar aceptación estática, acciones dirigidas, contacto, GUI, Player e inferencia real. Un esquema de acciones acotadas o un ensayo sin IA no prueba autonomía completa del modelo. Para comparación de normales sin tolerancias universales, consultar la [guía de métricas conjuntas](https://github.com/extremedan360/Design3dOptimizer/blob/b7ee70c8d10d3f949df2b3940ee98e65d78aa2c6/docs/reviews/uv-materiales-normales.md) y su helper original.
