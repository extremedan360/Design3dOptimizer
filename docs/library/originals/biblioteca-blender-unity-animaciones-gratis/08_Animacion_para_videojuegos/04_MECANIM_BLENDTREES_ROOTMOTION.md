# Mecanim, Blend Trees y Root Motion

## Animator Controller
- Estados iniciales: Idle, Locomotion, Jump, Interact y Hit.
- Parámetros: Speed (float), IsGrounded (bool), Interact (trigger), Hit (trigger).
- Define transiciones con condiciones y duración corta donde la respuesta del jugador sea prioritaria.
- Evita transiciones ambiguas que puedan bloquear el input.

## Blend Tree
- Usa 1D para Idle/Walk/Run por Speed.
- Usa 2D cuando necesites movimiento direccional y strafing.
- Ajusta thresholds tras medir velocidad real del controlador.

## Root Motion
- Con Root Motion, la animación puede impulsar el desplazamiento del personaje.
- Sin Root Motion, el script o controlador mueve el personaje y la animación acompaña.
- No mezcles ambos sin un criterio explícito: causa deslizamiento o movimiento doble.

## Interacción de gameplay
- Usa un estado de interacción que se dispare por una condición validada (distancia, objetivo, entrada).
- Comprueba que el trigger llegue al Animator, que la transición exista y que el clip esté asignado.

Fuentes: https://docs.unity3d.com/Manual/class-AnimatorController.html ; https://docs.unity3d.com/Manual/class-BlendTree.html ; https://docs.unity3d.com/Manual/RootMotion.html
