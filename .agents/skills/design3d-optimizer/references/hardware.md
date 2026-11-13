# Hardware, memoria y render

RAM y VRAM dedicada son presupuestos distintos. Liberar RAM no convierte 4 GB de GPU en 8 GB. Working sets comparten páginas: no sumarlos como consumo exclusivo.

Una etapa por vez, copia guardada, render inicial 512 px, pocas muestras/denoise y rebotes acotados si los materiales lo permiten. Aumentar resolución/detalle solo tras observar. Reducir muestras afecta sobre todo tiempo; no garantiza resolver OOM de texturas/modelos. Evitar cargar motor, Cycles y servidor de IA simultáneamente si compiten por memoria.

RGBA8 2048×2048 ocupa unos 16 MiB sin comprimir; mipmaps completos añaden aproximadamente un tercio. Formato y compresión GPU cambian el cálculo. Tamaño PNG en disco no equivale a memoria residente.

Registrar aplicación/versión, GPU, escena, resolución y técnica. Muestrear RAM del proceso y GPU total; etiquetar máximo como observado e intervalo. Puede perder picos cortos y la GPU incluye otras aplicaciones. Registrar tiempo, materiales/draw calls, transparencia y skin en el motor, además de memoria.

## StableGen

Código revisado: `68f2d165fdcdead669d322a86e6dc39887381354`. Trabaja con ComfyUI local/remoto. Admite argumentos extra como --lowvram, resolución 512 TRELLIS.2 y descarga de modelos entre etapas. Eso no demuestra compatibilidad con 4 GB.

Documentación consultada recomienda ~8 GB VRAM para SDXL y 16 GB o más para Qwen. Bajar polígonos después de generar no reduce la memoria de inferencia. Producir en otro PC y editar/exportar localmente es una alternativa, cuya conexión también debe probarse.

Posteriormente se verificó TRELLIS.2 nativo de ComfyUI usando el constructor de grafo StableGen, por etapas y con GPU de 4 GB/16 GB RAM: muestreo INT8/BF16 en GPU, decodificación CPU FP32 y servidor nuevo entre fases. Máximo GPU total observado 3.095 MiB. Eso prueba ese flujo y versiones, no todo el panel StableGen, cualquier resolución ni SDXL/Qwen. Ver [procedimiento y medidas](https://github.com/extremedan360/Design3dOptimizer/blob/main/docs/reviews/stablegen-trellis2-4gb.md).

Conservar perfiles y pesos SDXL si el usuario lo solicita; conservarlos en disco no exige cargarlos automáticamente. En el ensayo local, SDXL original y FP8 quedaron preservados, pero las cargas se interrumpieron por presión de RAM: no se considera un flujo SDXL completo aceptado para 4 GB. StableGen, el backend de generación 3D y SDXL para imágenes/texturas son componentes distintos. Verificar versiones y licencias antes de distribuir recursos; no publicar checkpoints por documentar un experimento.
