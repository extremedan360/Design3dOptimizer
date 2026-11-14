# Límites de `-noUpm` en una prueba con URP

Lección de un ensayo acotado con Unity 6000.6.8f1 sobre Windows. No distribuye código, recursos, rutas personales ni configuración de un proyecto. El objetivo era evaluar una variante de arranque de QA; su rechazo se conserva como resultado útil, sin convertirlo en recomendación universal.

## Contrato documentado y su alcance

La [referencia oficial de argumentos del Editor para Unity 6000.6](https://docs.unity.com/en-us/engine/6000.6/manual/unity-editor/command-line-arguments/editor) indica que `-noUpm` desactiva Unity Package Manager. Esa descripción no garantiza que un proyecto con dependencias ya resueltas conserve todos sus assemblies disponibles ni que pueda ejecutarse sin gestionar paquetes. Tampoco promete ahorro de RAM.

Distinguir tres estados: manifiesto y lock del grafo de paquetes; contenido disponible de paquetes; assemblies generados que la compilación necesita. Que los dos primeros existan no demuestra que el tercero sea válido bajo otro modo de arranque. Esta distinción evita confundir “ya resuelto” con “independiente del gestor”.

## Resultado observado

Se añadió únicamente `-noUpm` a un lanzamiento gráfico de QA aislado, con los paquetes previamente resueltos. Se fijaron antes y después manifiesto, lock y DLL de render pipeline, además de las fuentes y el comando. Los límites de memoria y la lógica de la prueba permanecieron iguales.

El proceso terminó antes de Play con errores CS0234 y CS0246: namespaces o tipos de URP/Core no estaban disponibles. Durante ese arranque Unity retiró DLL generadas que formaban parte de la preimagen observada. Las fuentes, el manifiesto y el lock permanecieron intactos. La comprobación posterior detectó DLL ausentes: el ensayo se rechazó, no se omitieron esos archivos para conseguir una verificación favorable.

Esto demuestra incompatibilidad de esa variante con ese estado concreto del proyecto y Editor. No demuestra que todo uso de `-noUpm` falle, ni identifica por sí solo cada decisión interna de recompilación o resolución de Unity.

## Recuperación y aprobación son resultados distintos

Se retiró el argumento y se volvió al arranque normal. Sin borrar manualmente cachés ni copiar DLL de otro proyecto, Unity regeneró los assemblies observados. Los quince archivos fijados —manifiesto, lock y DLL seleccionadas— recuperaron hashes idénticos a sus preimágenes. Eso acredita recuperación de ese conjunto, no de toda Library ni de cualquier entorno.

La ejecución normal posterior se detuvo por la guardia de RAM antes de Play. Por tanto, el estado de paquetes se recuperó, pero la prueba nativa no pasó. Conservar por separado el fallo de compilación con el argumento, la comprobación de recuperación y el aborto posterior de recursos. No reclasificar ninguno como PASS por haber recuperado sus DLL.

## Aplicación práctica

Antes de ensayar un argumento de arranque, usar un clon y registrar comando completo, fuentes, paquetes y salidas generadas pertinentes. Declarar qué puede cambiar y qué debe conservarse. Un fallo temprano debe conservar su log, código de salida y comparación con la preimagen, sin modificar fuentes para eliminar la dependencia que se intentaba observar.

Si faltan paquetes o assemblies, rechazar el ensayo y volver al modo conocido; no ocultar errores de compilación, bajar la guardia de recursos o injertar binarios ajenos. La presencia de una caché no permite asumir que un modo sin gestor será funcional.

Comparar memoria sólo entre ejecuciones equivalentes que alcanzan las mismas fases y cobertura. Una salida antes de Play puede consumir menos porque no ejecutó la escena: no es evidencia de optimización. En este caso no se estableció ahorro causal ni una alternativa offline validada.
