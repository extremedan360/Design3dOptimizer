# Animación de gameplay: acciones y ciclos

## Conjunto base
Idle, walk, run, sprint, jump-start, airborne, land, attack, hit-react, death e interact. Crea únicamente las acciones que el juego necesite.

## Ciclos
- Mantén el mismo punto de contacto entre primer y último fotograma de walk/run.
- Comprueba deslizamiento de pies en el motor, no solo en Blender.
- Conserva orientación y velocidad coherentes; define si el desplazamiento viene de Root Motion o del controlador del personaje.
- Usa nombres inequívocos: `CHR_Hero_Walk_Fwd`, `CHR_Hero_Interact_Pedestal`.

## Timing
- Trabaja con una tasa de fotogramas consistente.
- Prioriza silueta, anticipación, acción y recuperación.
- Para gameplay, deja claras las ventanas de impacto y cancelación; implementa los eventos críticos del lado de la lógica de juego.

## Organización
- Una acción reutilizable por clip cuando corresponda.
- Usa Action Editor y NLA para administrar y previsualizar secuencias.
- Verifica looping, transiciones y clips separados tras importar.

Referencia: https://docs.blender.org/manual/en/latest/editors/nla/index.html
