# TRELLIS.2 por etapas en 4 GB de VRAM

Ensayo original: 2026-11-12. ComfyUI 0.45.0 (c1eece62), StableGen 68f2d165, PyTorch 2.7.1+cu126, Windows, RTX 3050 Ti Laptop 4 GB y 16 GB RAM. No se publican la imagen ni el modelo privados del ensayo.

## Resultado y alcance

Se completó imagen a geometría y color nativos TRELLIS.2 en ese equipo, reutilizando el constructor de grafo de StableGen con checkpoints intermedios. Máximo GPU total observado: 3.095 MiB; RSS máximo de un proceso servidor: 4.675,6 MiB; RAM disponible mínima: 4.824,5 MiB entre las etapas exitosas registradas. El muestreo puede perder picos; RSS incluye páginas compartidas y GPU incluye otras aplicaciones. No son medidas de un videojuego ni promesas para cualquier equipo de 4 GB.

La salida original tuvo 2.951.728 triángulos. Generación completada no equivale a retopología aceptada: había paredes interiores, cruces y bordes no manifold. Se entregó alta densidad y RGB por vértice, sin rig ni atlas UV final. Las reducciones y remallas no dieron una versión aceptable para juego.

## Separar la memoria de cada fase

1. Quitar fondo y guardar imagen encuadrada.
2. Ejecutar DINO y guardar condicionamientos positivo/negativo en CPU.
3. Muestrear estructura en GPU y guardar latente.
4. Decodificar estructura en CPU y guardar vóxeles.
5. Muestrear forma en GPU y guardar latente y coordenadas.
6. Decodificar forma en CPU; guardar malla y subdivisiones.
7. Muestrear material en GPU con el submodelo de textura.
8. Decodificar material en CPU usando las subdivisiones.
9. Aplicar color con PaintMesh. UV/baking es otra fase, no validada sobre una retopología aceptada.

Cerrar el proceso entre fases libera referencias y cachés. Serializar tensores y contenedores sencillos, cargar con weights_only=True y validar formato/rutas. Conservar samples, coords, coord_counts, coord_resolution y model_frame: guardar solo samples pierde información espacial.

Las guías de subdivisión usan ocho signos por vóxel. En esta versión el decoder consume feats > 0: máscaras BOOL, coordenadas int32, shape y escala racional conservaron exactamente sus decisiones en roundtrip. No guardar cachés de vecinos ni clases arbitrarias. Mantener el marco original de las guías; malla y vóxeles de color se convierten al marco glTF en pasos distintos.

## Pesos y precisión

El checkpoint oficial INT8 ConvRot ocupa 5.253.048.192 bytes. Se copiaron sus tensores y metadatos, sin recuantizar, a dos perfiles: forma sin shape2txt (3.939.677.784 bytes) y solo textura (1.313.369.368 bytes). El detector nativo reconoce presencia/ausencia del submodelo. Conservar las configuraciones de cuantización de cada capa y verificar hashes/bytes retenidos.

BF16/FP16 INT8 ConvRot pasaron una prueba pequeña CUDA usando el backend eager instalado. Eso solo no probaba inferencia completa; las fases completas se verificaron después. No se cambió el controlador ni PyTorch global.

En este Ryzen, CPU FP32 resultó más rápido que BF16: la estructura terminó en 3,79 s; el intento BF16 seguía trabajando cuando se detuvo a 193 s. No es un benchmark universal. Reducir bits no siempre mejora el trabajo CPU.

La opción cpu-vae no bastó: los nodos nativos escogían activaciones CUDA mediante get_torch_device() mientras los pesos estaban en CPU. Un adaptador local ejecutó el decoder nativo realmente en CPU, restaurando el estado en finally, en servidor dedicado de un trabajo. No aplicar ese estado global a ejecuciones concurrentes sin aislamiento.

## Calidad y fallos que no deben ocultarse

- El QEM inicial hacia 60k dañó contorno y conectividad. RAW tenía 378.008 bordes con más de dos caras; no era una superficie cerrada sencilla.
- Shade smooth o remalla no garantizan reparar una doble pared. Se descartaron candidatos con agujeros aunque cumplieran el presupuesto numérico.
- Make Solid completo se interrumpió a 300,44 s por tiempo, con 3.838,8 MiB de RAM observada. No fue OOM ni prueba imposibilidad de reparación.
- PaintMesh exportó solo RGB por vértice. No describir el GLB como atlas PBR: rugosidad/metallic permanecieron en el caché de vóxeles.
- Un bloqueo inicial de sockets internos de asyncio ocurrió antes de cargar modelos en un entorno restringido. El volcado de pila lo distinguió de OOM; la API local necesitó el permiso correspondiente, sin cambiar seguridad global.

## Fuentes

[StableGen: generación](https://github.com/sakalond/StableGen/wiki/TRELLIS.2-mesh-generation), [ComfyUI: TRELLIS.2 nativo e INT8](https://docs.comfy.org/tutorials/3d/trellis2), [Microsoft: implementación original](https://github.com/microsoft/TRELLIS.2).

Los requisitos de Microsoft no deben extrapolarse como mínimos medidos del port ComfyUI. Este caso tampoco prueba todo el panel StableGen, SDXL/Qwen, rig automático o cualquier resolución en 4 GB. La entrada era pequeña y las vistas ocultas se infirieron. Revalidar versión, calidad, memoria y destino de juego.
