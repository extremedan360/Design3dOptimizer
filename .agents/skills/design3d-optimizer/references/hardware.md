# Hardware, memoria y render

RAM y VRAM dedicada son presupuestos distintos. Liberar RAM no convierte 4 GB de GPU en 8 GB. Working sets comparten páginas: no sumarlos como consumo exclusivo.

Una etapa por vez, copia guardada, render inicial 512 px, pocas muestras/denoise y rebotes acotados si los materiales lo permiten. Aumentar resolución/detalle solo tras observar. Reducir muestras afecta sobre todo tiempo; no garantiza resolver OOM de texturas/modelos. Evitar cargar motor, Cycles y servidor de IA simultáneamente si compiten por memoria.

RGBA8 2048×2048 ocupa unos 16 MiB sin comprimir; mipmaps completos añaden aproximadamente un tercio. Formato y compresión GPU cambian el cálculo. Tamaño PNG en disco no equivale a memoria residente.

Registrar aplicación/versión, GPU, escena, resolución y técnica. Muestrear RAM del proceso y GPU total; etiquetar máximo como observado e intervalo. Puede perder picos cortos y la GPU incluye otras aplicaciones. Registrar tiempo, materiales/draw calls, transparencia y skin en el motor, además de memoria.

## StableGen

Código revisado: `68f2d165fdcdead669d322a86e6dc39887381354`. Trabaja con ComfyUI local/remoto. Admite argumentos extra como --lowvram, resolución 512 TRELLIS.2 y descarga de modelos entre etapas. Eso no demuestra compatibilidad con 4 GB.

Documentación consultada recomienda ~8 GB VRAM para SDXL y 16 GB o más para Qwen. Bajar polígonos después de generar no reduce la memoria de inferencia. Producir en otro PC y editar/exportar localmente es una alternativa, cuya conexión también debe probarse. No se instalaron ni validaron modelos StableGen en este caso. Verificar versiones y licencias antes de distribuir recursos.
