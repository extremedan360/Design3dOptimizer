# SD1.5 por componentes

Texto, muestreo y VAE se ejecutan en procesos sucesivos de ComfyUI, con archivos intermedios verificados. El grafo procede del flujo común de StableGen adaptado a cargadores explícitos. No ejecuta todo su panel ni acredita SDXL o multivista.

## Entorno comprobado

Windows, Python 3.12, ComfyUI 0.45.0 (`c1eece62cbf1805d4f64286d7f5592e6a215e6ba`), PyTorch 2.7.1+cu126, NVIDIA y `psutil`. El entorno de ComfyUI debe disponer también de `safetensors`. Se observó una RTX 3050 Ti de 4 GB, controlador 566.36 y 16 GB de RAM. Son versiones del ensayo, no mínimos garantizados; otro entorno necesita revisar flags y compatibilidad.

Use un entorno existente y sus dependencias revisadas. Estos scripts no instalan nada globalmente ni descargan pesos. `split_checkpoint.py` y el preparador usan biblioteca estándar; `run_phase.py` y `run_guard.py` necesitan `psutil`. El plugin se carga dentro del proceso de ComfyUI y usa su PyTorch/safetensors.

## Preparar

Desde esta carpeta, sustituya los ejemplos siguientes por rutas absolutas propias. Particiones, salida y evidencias deben ser destinos nuevos; no cree sus carpetas finales antes de ejecutar cada herramienta. Las particiones deben quedar fuera de la carpeta del checkpoint original y la salida fuera de ComfyUI. Mantenga libre el puerto elegido y no ejecute varias fases a la vez.

```powershell
$ComfyPython = 'X:\tools\comfy-env\Scripts\python.exe'
$ComfyRoot = 'X:\tools\ComfyUI'
$ModelSource = 'X:\models\source\v1-5-pruned-emaonly-fp16.safetensors'
$SplitRoot = 'X:\models-split\sd15-fp16'
$RunRoot = 'X:\sd15-runs\trial01'
$EvidenceRoot = 'X:\sd15-evidence\trial01'

& $ComfyPython -B split_checkpoint.py --help
& $ComfyPython -B prepare_stages.py prepare --help
& $ComfyPython -B run_phase.py --help
& $ComfyPython -B run_guard.py --help

& $ComfyPython -B split_checkpoint.py --source $ModelSource --output $SplitRoot --expected-sha256 e9476a13728cd75d8279f6ec8bad753a66a1957ca375a1464dc63b37db6e3916
& $ComfyPython -B prepare_stages.py prepare --baseline baseline.json --models $SplitRoot --comfy $ComfyRoot --python $ComfyPython --run $RunRoot --port 8188 --vae-decode full
```

Verifique `$LASTEXITCODE` tras cada invocación y deténgase ante un error. La partición conserva bytes, dtypes y auxiliares; no cuantiza ni entrena. Se exige el checkpoint SD1.5 FP16 fijado en el [resumen](../../docs/evidencias/sd15-staged/resumen.json). El baseline mantiene 512×512, lote1, semilla131113, 20pasos, Euler, CFG5,5 y denoise1. Sólo su prefijo de salida se ha generalizado; no sustituya parámetros silenciosamente.

El preparador crea grafos, configuración por proceso, caché aislada y comandos vinculados por hashes. No inicia inferencia. El decode completo CPU es predeterminado. `--vae-decode tiled128` conserva la comparación diagnóstica de bloques128/solape32: completó técnicamente, pero su imagen fue rechazada por discontinuidades.

## Ejecutar una fase cada vez

```powershell
& $ComfyPython -B run_guard.py --out (Join-Path $EvidenceRoot 'phase1') --timeout 720 -- $ComfyPython -B run_phase.py $RunRoot 1
```

Antes de continuar, revise `phase1/result.json` dentro del ensayo y `phase1/resources.json` dentro de evidencias: ambos deben indicar éxito y cierre del árbol propio. La primera fase guarda condicionamientos CPU tipados con recibo SHA, sin pickle.

```powershell
& $ComfyPython -B run_guard.py --out (Join-Path $EvidenceRoot 'phase2') --timeout 720 -- $ComfyPython -B run_phase.py $RunRoot 2
```

Revise del mismo modo los dos informes de fase2. Obtenga la ruta exacta del latente desde `phase2/result.json`, en `outputs`, sección `latents`; no adivine otro archivo. Para la primera salida del baseline, la ruta habitual es:

```powershell
$LatentSource = Join-Path $RunRoot 'output\staged-sd15\sampled_00001_.latent'
& $ComfyPython -B prepare_stages.py bind-latent --run $RunRoot --source $LatentSource
& $ComfyPython -B run_guard.py --out (Join-Path $EvidenceRoot 'phase3') --timeout 720 -- $ComfyPython -B run_phase.py $RunRoot 3
```

Compruebe el éxito del bind antes de fase3. La vinculación verifica forma F32 `[1,4,64,64]`, hash y marcador nativo de escala. No sobrescribe un vínculo existente. Texto/muestreo usan GPU; el VAE completo usa CPU FP32. Se espera el cierre de cada árbol propio antes del siguiente. El guard conserva 2GiB de RAM disponible y 3.600MiB de GPU total, con muestreo aproximado de0,75s más consultas: puede perder picos. Un fallo se conserva y no autoriza bajar umbrales, cerrar aplicaciones ajenas o reutilizar un servidor ocupado.

## Inspección y límites

Revise informes y píxeles: ejecución correcta no equivale a textura aceptada. El decode completo aceptado reutilizó el mismo latente del ensayo por bloques, sin volver a muestrear. Una recuperación para compararlos debe preparar un destino separado y vincular explícitamente ese mismo latente; no edite grafos ya congelados ni copie archivos sin sus hashes.

Consulte la [guía de integración](../../docs/reviews/integracion-texturas-generadas.md) antes de aplicar el mapa en motor. No se garantiza encaje en cualquier GPU4GB, contacto corporal, PBR físicamente medido ni rendimiento del juego. No publique los logs de ejecución sin sanear: contienen rutas locales e identificadores de procesos.

Los pesos conservan CreativeML OpenRAIL-M y StableGen GPL-3.0; las utilidades originales de esta biblioteca MIT. La licencia del ejemplo no relicencia pesos ni dependencias. No se incluyen modelos, imágenes, cachés o recursos de otros proyectos.
