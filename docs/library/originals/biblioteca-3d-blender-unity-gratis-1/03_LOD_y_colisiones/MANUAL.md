# LOD y colisiones

## LOD
1. Genera LOD0 de máxima calidad necesaria.
2. Simplifica primero detalles internos y piezas diminutas.
3. Preserva silueta y normales; evita saltos visuales notorios.
4. Configura LOD Group en Unity y prueba transiciones desde la cámara real.
5. Verifica si el coste de LOD extra compensa memoria y mantenimiento.

## Colisiones
Prefiere primitivas o colliders compuestos sencillos cuando sea viable. Reserva Mesh Collider para geometrías que realmente lo exijan; verifica si es convexo y si hay cuerpos dinámicos.

## Escenas
Evalúa instancing, batching, occlusion culling y número de materiales. No combines todos los objetos indiscriminadamente: puedes perjudicar culling y memoria.
