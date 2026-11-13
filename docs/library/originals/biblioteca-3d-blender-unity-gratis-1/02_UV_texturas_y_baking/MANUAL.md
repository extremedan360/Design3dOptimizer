# UV, texturas PBR y baking

## UV
1. Marca costuras en áreas poco visibles.
2. Reduce estiramiento y controla densidad de texel.
3. Mantén padding suficiente para mipmaps.
4. Comparte atlas cuando reduzca cambios de material sin degradar demasiado la calidad.

## Texturas
- Base Color: información de color, sin iluminación horneada salvo intención artística.
- Normal: detalle de superficie; valida convención de canales en el motor.
- Metallic/Roughness: comprueba el mapeo de canales y el shader usado en Unity.
- Ambient Occlusion: opcional; revisa cómo se combina en el material.

## Baking
Crea high-poly y low-poly, UV del low-poly, bake de normales/AO y prueba con iluminación real en Unity. Revisa artefactos en costuras, tangentes y normales.

## Rendimiento
La resolución y compresión deben definirse por dispositivo objetivo. Usa mipmaps para texturas 3D habituales; evita asumir que 4K es siempre mejor.
