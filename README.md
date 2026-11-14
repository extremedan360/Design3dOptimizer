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

Para una instalación de usuario disponible entre proyectos, instalar la carpeta completa de la habilidad con el instalador de habilidades compatible con tu versión de Codex. Conservar además un clon estable de este repositorio y vincularlo mediante `local-library.json`; ver [biblioteca compartida](.agents/skills/design3d-optimizer/references/biblioteca-compartida.md). No incluir esa configuración personal en commits. La sincronización y el aprendizaje ocurren durante tareas activas; no hay entrenamiento del modelo o servicio en segundo plano.

## Principios

- Probar primero una etapa pequeña y guardar copias del original.
- En personajes, revisar la base sin ropa ni complementos; después integrar cada pieza con tamaño, sujeción y función coherentes. Ejemplo: animal → adorno de cabeza → mochila.
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

- [TRELLIS.2 por etapas en 4 GB](docs/reviews/stablegen-trellis2-4gb.md): inferencia local verificada y límites de topología/calidad.
- [Reparación de superficies generadas](docs/reviews/reparacion-superficie-generada.md): volumen sin signo, retopología, materiales y pelaje por etapas con mediciones.
- [Integración de texturas generadas](docs/reviews/integracion-texturas-generadas.md): autoridad visual tras el arranque, texturas de autor y paleta; diagnóstico de RAM/VRAM y carga de SD1.5 por componentes, con pruebas por etapas y límites documentados.
- [Materiales, complementos y exportación](docs/reviews/materiales-accesorios-y-exportacion.md): base antes de accesorios, sujeción funcional, cuero/tela, ojos, skin y límites comprobados de GLB/LOD.
- [Expresiones, párpados y pelaje: lecciones verificadas](docs/reviews/expresiones-y-pelaje.md): cobertura ocular, controles independientes y separación entre presentación y juego.
- [Rig independiente y modular](docs/reviews/cuy-rig-independiente-y-modular.md): lecciones de un personaje con 31 huesos de deformación y seis clips de tres segundos; separar controles, piezas y evidencias de exportación sin incorporar assets de otro juego.
- [Biblioteca Blender + Unity + Animación](docs/library/README.md): tres ZIP, 46 entradas analizadas, 34 documentos únicos y 33 URLs catalogadas; originales preservados con SHA-256 y duplicados deduplicados. Ver [análisis y límites](docs/library/ANALISIS.md).
- [Revisión de DESIGN:OS 3D Blender y sus perfiles](docs/reviews/design-os-3d-blender.md): utilidad, ámbitos y licencias; no se copió su implementación.

## Ejemplo y herramientas

[Cuy aventurero](examples/cuy/README.md): generación por etapas, dos representaciones de pelo, huesos y demostración animada. Código, vistas y medidas; los artefactos pesados se generan localmente.

```sh
python scripts/glb_report.py personaje.glb
blender --background personaje.blend --python scripts/asset_report.py -- --output informe.json
blender --background --factory-startup --python-exit-code 2 --python scripts/modular_report.py -- --file personaje.glb --output modular.json
```

`modular_report.py` inventaría mallas, jerarquía, materiales, morphs y vínculos de armature en el frame actual. Contar objetos separados no acredita independencia semántica, ajuste o rendimiento. El nuevo [ejemplo StableGen modular](examples/stablegen-modular/README.md) completó cinco etapas reales a resolución 512 con INT8/MPS. Tras reparación unsigned y modelado separado de mochila, brote, ojos y herrajes en Blender, el ensamble exploratorio estático tiene 16.952 triángulos. No incorpora rig ni animaciones nuevos. La revisión exploratoria en Blender y tras reimportar el GLB aceptó avanzar: 18 mallas, siete materiales, cero imágenes y 421.076 bytes; el cuerpo quedó cerrado, con cinco tubos abiertos de accesorios aún pendientes de limpieza. No acredita fidelidad exacta o FPS móviles. Los fallos de reparación y límites se registran junto a la evidencia, sin trasladar las cifras del caso articulado anterior.

Python 3 para utilidades externas; Blender para `bpy`. Ejemplo probado con Blender 5.2.3 LTS. No se promete compatibilidad no comprobada.

## Colaboración

Lee [CONTRIBUTING.md](CONTRIBUTING.md). Hacer fetch/pull antes de incorporar aprendizajes; validar cambios, crear commits breves y descriptivos y verificar el push autorizado. No existe un servicio que observe otros chats o publique automáticamente en segundo plano. Cada sesión que use esta base debe sincronizar y registrar los aprendizajes pertinentes.

Código/documentación originales bajo [MIT](LICENSE). Referencias externas conservan sus licencias. No se incluyen transcripciones completas ni la imagen privada de referencia del personaje.
