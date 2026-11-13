# Design3D Optimizer

Agente reutilizable y biblioteca práctica para **crear recursos 3D de videojuegos con calidad visual y costes medidos**: vegetación, estructuras, escenarios, objetos, seres vivos, rigs, acciones, animaciones y efectos visuales. El cuy es un ejemplo, no el alcance completo.

Reusable, measured Blender workflows for game assets, vegetation, environments, characters, animation and VFX. Documentation is primarily in Spanish. Scripts and examples are inspectable and portable.

## Empezar

```sh
git clone https://github.com/extremedan360/Design3dOptimizer.git
cd Design3dOptimizer
git pull --ff-only origin main
```

En Codex, abre esta carpeta y solicita:

> Usa $design3d-optimizer para crear un cuadrúpedo con mochila, parpadeo y pelaje corto. Comprueba el equipo, trabaja por etapas y entrega medidas y un GLB verificable.

La habilidad está en [.agents/skills/design3d-optimizer](.agents/skills/design3d-optimizer/SKILL.md). Si la aplicación no la descubre, pide al agente que lea ese archivo. En otro proyecto, copia la carpeta completa `design3d-optimizer` a su `.agents/skills/`, incluyendo referencias y metadatos. No reemplaces sus instrucciones particulares. Los scripts y ejemplos pueden ejecutarse desde este clon; no son dependencias necesarias de la habilidad.

Otros asistentes pueden leer [AGENTS.md](AGENTS.md) y la habilidad. Clonar no instala modelos, Blender ni servicios. Esto es conocimiento y herramientas, no una IA entrenada ni una API de agentes.

## Principios

- Probar primero una etapa pequeña y guardar copias del original.
- Mejorar silueta y deformación con geometría; usar normales/texturas para microdetalle.
- Separar presentación de recurso de juego: un render de hebras no demuestra el acabado ni FPS de tarjetas.
- Medir RAM, VRAM, geometría, materiales y duración; documentar límites del muestreo.
- Reimportar y probar expresiones/poses; distinguir física horneada de simulación interactiva.

## Guías

| Necesidad | Referencia |
| --- | --- |
| Vegetación, estructuras, seres vivos y VFX | [Recursos para videojuegos](.agents/skills/design3d-optimizer/references/recursos-videojuegos.md) |
| Acciones, clips, transiciones e IK | [Animación](.agents/skills/design3d-optimizer/references/animacion.md) |
| UV, colisiones y perfilado en motor | [Pipeline de juego](.agents/skills/design3d-optimizer/references/pipeline-juego.md) |
| Forma, sombreado, materiales | [Modelado](.agents/skills/design3d-optimizer/references/modelado.md) |
| Tarjetas, capas, curvas y física de pelo | [Pelaje](.agents/skills/design3d-optimizer/references/pelaje.md) |
| Huesos, pesos, boca y parpadeo | [Rigging](.agents/skills/design3d-optimizer/references/rigging.md) |
| 4 GB de VRAM y StableGen | [Hardware](.agents/skills/design3d-optimizer/references/hardware.md) |
| Reducción y niveles de detalle | [Retopología](.agents/skills/design3d-optimizer/references/retopologia.md) |
| GLB/FBX y validación | [Exportación](.agents/skills/design3d-optimizer/references/exportacion.md) |
| Incorporar nuevos conocimientos | [Aprendizaje](.agents/skills/design3d-optimizer/references/aprendizaje.md) |
| Videos y documentación consultada | [Fuentes](.agents/skills/design3d-optimizer/references/fuentes.md) |

## Biblioteca aportada y revisiones

- [Biblioteca Blender + Unity + Animación](docs/library/README.md): tres ZIP, 46 entradas analizadas, 34 documentos únicos y 33 URLs catalogadas; originales preservados con SHA-256 y duplicados deduplicados. Ver [análisis y límites](docs/library/ANALISIS.md).
- [Revisión de DESIGN:OS 3D Blender y sus perfiles](docs/reviews/design-os-3d-blender.md): utilidad, ámbitos y licencias; no se copió su implementación.

## Ejemplo y herramientas

[Cuy aventurero](examples/cuy/README.md): generación por etapas, dos representaciones de pelo, huesos y demostración animada. Código, vistas y medidas; los artefactos pesados se generan localmente.

```sh
python scripts/glb_report.py personaje.glb
blender --background personaje.blend --python scripts/asset_report.py -- --output informe.json
```

Python 3 para utilidades externas; Blender para `bpy`. Ejemplo probado con Blender 5.2.3 LTS. No se promete compatibilidad no comprobada.

## Colaboración

Lee [CONTRIBUTING.md](CONTRIBUTING.md). Hacer fetch/pull antes de incorporar aprendizajes; validar cambios, crear commits breves y descriptivos y verificar el push autorizado. No existe un servicio que observe otros chats o publique automáticamente en segundo plano. Cada sesión que use esta base debe sincronizar y registrar los aprendizajes pertinentes.

Código/documentación originales bajo [MIT](LICENSE). Referencias externas conservan sus licencias. No se incluyen transcripciones completas ni la imagen privada de referencia del personaje.
