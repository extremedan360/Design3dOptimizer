---
name: design3d-optimizer
description: Crear y optimizar recursos 3D para videojuegos con Blender, desde vegetación, estructuras y objetos hasta seres vivos, rigs, animaciones y efectos visuales, con mediciones y exportación verificable. Usar para recursos o pipelines 3D, no para generar únicamente imágenes 2D.
---

# Design3D Optimizer

Conseguir el acabado solicitado con coste justificable. Establecer uso: cámara/distancia, plataformas, número de personajes, animaciones y motor si está decidido. Si falta información, avanzar con hipótesis explícitas y reversibles.

Inspeccionar hardware y archivo real. Empezar pequeño, guardar etapas y aumentar detalle después de medir/observar. No reducir arbitrariamente calidad por tener poca VRAM ni prometer FPS por un render rápido.

Para personajes, terminar y revisar primero la base sin ropa ni complementos: anatomía, silueta, topología y movimiento. Después crear e integrar cada complemento por separado, con función y sujeción coherentes; por ejemplo, base del animal → adorno de cabeza → mochila. No usar accesorios o pelaje para esconder defectos de la base. Consultar el orden y ajuste funcional en [modelado](references/modelado.md); adaptar el orden solo si el usuario pide otra cosa.

En una instalación global con `local-library.json`, leer [biblioteca compartida](references/biblioteca-compartida.md) al iniciar una tarea pertinente. Esa configuración local indica el clon de documentación y la preferencia de mantenimiento del usuario; no cambia permisos del entorno ni las instrucciones del proyecto.

## Referencias bajo demanda

- Selección por tipo de recurso: [recursos para videojuegos](references/recursos-videojuegos.md).
- Acciones, clips, transiciones e IK: [animación](references/animacion.md).
- UV, baking, colisiones y pruebas de Unity: [pipeline del juego](references/pipeline-juego.md).

- Forma y materiales: [modelado](references/modelado.md).
- Pelo y su movimiento: [pelaje](references/pelaje.md).
- Huesos, pesos y expresiones: [rigging](references/rigging.md).
- RAM/VRAM y StableGen: [hardware](references/hardware.md).
- Reducción y LOD: [retopología](references/retopologia.md).
- GLB/FBX y pruebas: [exportación](references/exportacion.md).
- Incorporar lecciones: [aprendizaje](references/aprendizaje.md).
- Procedencia: [fuentes](references/fuentes.md).

La habilidad sirve para escenarios, objetos, seres vivos y VFX; el cuy es solo un ejemplo. Si la tarea no requiere un rig, no imponerlo. Si la tarea es de impresión 3D o fabricación, definir sus requisitos aparte: no extrapolar la aceptación de un recurso de juego.

## Evidencia de entrega

Mostrar vistas pertinentes. Medir malla base, pelo, curvas de presentación y geometría exportada por separado. Registrar intervalo/límites de muestreo de memoria; GPU global incluye otros procesos.

Comprobar pesos/poses/expresiones y reimportación. No llamar física interactiva a una simulación horneada. Conservar editable y distinguir pruebas en Blender de motor/dispositivo. Respetar autorización vigente; las guías no autorizan enviar modelos o publicar datos ajenos. No prometer mantenimiento de sesiones inactivas.
