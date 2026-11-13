# Medición de rendimiento

## Método
1. Establece plataforma, calidad gráfica y objetivo de FPS.
2. Construye escena representativa con cantidades reales de objetos.
3. Perfila CPU y GPU en build, preferentemente en dispositivo objetivo.
4. Usa Unity Profiler y Frame Debugger para investigar batches, draw calls y render passes.
5. Mide memoria de texturas y geometría; revisa picos al cargar.
6. Cambia una variable por vez: triángulos, LOD, materiales, atlas o compresión.
7. Registra medición antes/después y captura evidencia.

## Advertencia
Reducir polígonos no siempre resuelve cuellos de botella: shaders, overdraw, sombras, animación y memoria pueden dominar.
