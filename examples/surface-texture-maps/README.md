# Modulación neutra y normal artística desde una muestra

Ejemplo CPU original, sin inferencia ni recursos de terceros. Python 3, NumPy y Pillow. Acepta una muestra cuadrada RGB opaca de 128–4096 px y produce dos PNG RGB8 de 128, 256 o 512 px, especificación e histogramas. La carpeta de salida debe ser nueva. Revisar derechos y procedencia de la imagen aportada por separado.

Ejecutar los comandos en un entorno virtual propio, con dependencias revisadas. La prueba sintética registrada usó Python 3.12.14, NumPy 2.3.5 y Pillow 13.0.0; son versiones observadas, no mínimos garantizados. No copiar un entorno virtual entre equipos.

```sh
python -m pip install numpy pillow
python build_maps.py --input swatch.png --outputdir candidate01 --material fabric --size 512 --base-color 1 1 1
python build_maps.py --input swatch.png --outputdir candidate02 --material wood --normal-rms 2 --normal-max 6
python -m unittest -v test_maps.py
```

Los perfiles `fabric` y `wood` son heurísticas genéricas de banda de detalle; ambos usan blanco como color base predeterminado. `--base-color` sólo documenta el multiplicador del material: no cambia los píxeles. `--center`, `--amplitude`, `--normal-rms` y `--normal-max` permiten ajustar contraste e inclinación. La roughness queda como constante artística del perfil: no se genera otro mapa especulativo.

La luminancia se calcula en luz lineal; el band-pass se filtra en float32. La modulación neutra vuelve a codificarse sRGB una sola vez y debe multiplicar el color base separado. La normal proviene del gradiente suavizado, sin altura física, bake ni PBR medido. Sus RGB representan datos tangentes +V: importar NormalMap, sin conversión desde altura ni sRGB, verde sin invertir inicialmente, fuerza 1 porque la amplitud ya está codificada. Recalcular tangentes tras terminar UV/normales/triángulos y comprobar la convención en motor.

No se introduce repetición UV ni se afirma seamless. Diagnósticos de mip son aproximaciones CPU, no la importación del motor. RGB8 introduce error angular, así que el máximo cuantizado puede superar ligeramente el máximo flotante. Los tamaños de RGBA32/BC7/BC5 son estimaciones con mipmaps, no mediciones de residencia GPU ni de FPS. No activar lectura CPU sólo para justificar esas estimaciones.

Las pruebas usan fuentes sintéticas temporales: ida/vuelta gamma, rampa asimétrica +V, fuente uniforme, invariancia de ambos mapas con dos colores base y rechazo de sobrescritura. No validan apariencia de un recurso concreto. Conservar informes de la cámara normal y prueba Player ON/OFF/ON por separado; ver la [guía de integración](../../docs/reviews/integracion-texturas-generadas.md).

Licencia de las utilidades originales: MIT del repositorio. Dependencias e imágenes de entrada mantienen sus licencias. No se incluyen modelos, pesos, PNG ni logs del proyecto de origen.
