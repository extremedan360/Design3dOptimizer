# Fundamentos de modelado para videojuegos

## Objetivo
Crear modelos legibles, eficientes y fáciles de editar.

## Proceso
1. Define silueta y escala antes de agregar detalle.
2. Modela bloques primarios y comprueba proporciones en cámara de juego.
3. Aplica Mirror cuando sea útil, evitando duplicación innecesaria.
4. Usa bevel solo donde altere reflejos o silueta.
5. Revisa normales, caras internas, geometría no-manifold y vértices duplicados.
6. Para personajes, diseña loops alrededor de articulaciones; prueba poses extremas.
7. Evalúa el modelo triangulado antes de exportar; las n-gons pueden triangularse de forma inesperada.

## Regla importante
No hay un presupuesto universal de triángulos. Establécelo según plataforma, tamaño en pantalla, número de instancias y medición en Unity.

## Ejercicio
Crea una caja, barril y roca; compara 3 variantes de geometría y su silueta a distancia.
