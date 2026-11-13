# IK, animación facial y optimización

## IK y Animation Rigging
- IK de pies para contacto con terreno; IK de manos para armas, herramientas o interacción.
- Usa constraints solo donde aporten mejora visible; comprueba costes en runtime.
- Revisa orden de ejecución con locomoción y root motion.

## Facial
- Shape Keys / Blend Shapes para expresiones y visemas.
- Limita cantidad y complejidad según plataforma.
- Valida importación de blend shapes y curvas en Unity.

## Rendimiento
- Reduce huesos y vértices influenciados cuando sea viable.
- Considera culling y LOD para personajes secundarios.
- Mide CPU/GPU, skinning, Animator y memoria con Profiler en hardware objetivo.
- Evita asumir que menos polígonos siempre es el cuello de botella.

Fuentes: https://docs.unity3d.com/Packages/com.unity.animation.rigging@latest ; https://docs.unity3d.com/Manual/Profiler.html ; https://docs.blender.org/manual/en/latest/animation/shape_keys/index.html
