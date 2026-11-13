# Análisis de las tres bibliotecas

## Cobertura real

Se leyeron todas las entradas textuales de los tres ZIP, incluidos índices, ejercicios, manuales, checklists y shortcuts. No contienen PDFs, ejecutables, modelos, rigs ni proyectos Unity. Las 33 URLs remiten a recursos externos más grandes; su catálogo no implica haber leído todo Blender, todo Unity o diez horas de un curso.

Se contrastaron páginas accesibles de LOD, perfilado, Fundamentals y el índice del curso Arm/Unity; otros enlaces devolvieron redirecciones o restricciones de acceso. Se registra ese límite en ENLACES. No se ejecutaron los ejercicios de Unity ni se instaló Animation Rigging.

## Aportes aprovechables

| Tema | Aporte de los apuntes | Cómo se integra |
| --- | --- | --- |
| Fundamentos/topología | Silueta, escala, normals, loops y triangulación | Ruta de modelado y criterios distintos por tipo de recurso |
| UV/PBR/bake | Texel density, padding, tangentes y canales | Pipeline de juego; separar normal map procedural de bake high-to-low |
| LOD/colisión | Coste/beneficio, proxies y culling | Vegetación y estructuras; no unir escenas indiscriminadamente |
| Rigging | Articulaciones, jerarquía, pesos y poses | Guía cuadrúpedo/general; comprobaciones reales en ejemplo |
| Animación | Acciones, NLA, clips, locomoción y eventos | Referencia de animación; demo no presentada como walk de producción |
| Blender→Unity | Ejes, escala, materiales, rig/importación | Prueba pequeña antes de lotes; elegir Generic/Humanoid correctamente |
| Mecanim/Blend Trees | Estados, parámetros, thresholds y Root Motion | Procedimiento de integración pendiente de motor real |
| IK/facial | Contactos, expresiones y orden de ejecución | Elegir por mejora visible y coste medido |
| Perfilado | CPU/GPU, memoria, Frame Debugger, escena real | Separar Cycles de gameplay; cambiar una variable por comparación |
| Automatización/MCP | Inventario y validación JSON | Herramientas de lectura/ejemplo por etapas; no asumir MCP instalado |

## Correcciones y matices necesarios

1. **Versiones:** Fundamentals corresponde a Blender 2.8; útil para extrude/loop cut/bevel/knife, no como contrato de API 5.2. El curso Arm/Unity consultado indica 2019.4; no trasladar sus menús o render pipeline a versiones actuales sin comprobar.
2. **Latest cambia:** fijar Blender, Unity y paquetes para reproducibilidad. `@latest` de Animation Rigging no es una versión estable para todos los proyectos.
3. **No-manifold:** puede ser intencional en tarjetas, planos y efectos de juego. Una malla no-manifold no es defecto universal; impresión/colisión cerrada tienen requisitos diferentes.
4. **Optimización:** reducir caras no garantiza menor coste dominante. Hojas, pelo y VFX pueden estar limitados por transparencia; estructuras por materiales/culling; personajes por Animator/skin.
5. **Root Motion:** declarar quién mueve al personaje. Probar velocidad/contactos en motor; no duplicar desplazamiento en animación y controlador.
6. **Rig:** pesos automáticos no aprueban deformación. Generic/Humanoid depende de anatomía; no mapear por defecto un cuy a humanoide.
7. **Materiales:** Unity depende del pipeline. Convención normal y roughness/smoothness necesitan conversión comprobada. Un GLB necesita un importador compatible; no asumir importación nativa en todo proyecto Unity.
8. **Física:** un clip de mochila oscilando no responde a contactos en partida. Horneado y simulación interactiva son entregas diferentes.
9. **LOD:** ahorra trabajo solo si compensa memoria/transición; cross-fade puede dibujar dos niveles temporalmente.
10. **Profiling:** target build/dispositivo, no solo Editor. Deep Profiling añade instrumentación; distinguir medición de investigación de un benchmark comparable.

## Aplicación y pruebas pendientes

El ejemplo del cuy prueba construcción por etapas, materiales portables, pelaje, pesos, morphs y reimportación animada en Blender. Su demo no prueba Mecanim, avatar Unity, Root Motion de controlador, IK, colisiones continuas o FPS en teléfono.

Vegetación, edificios, VFX y otros seres vivos tienen rutas documentadas, no ejemplos funcionales de todos ellos. Añadir evidencia por categoría a medida que se realicen tareas concretas, sin declarar que una biblioteca escrita ya construyó todos esos sistemas.

## Mantenimiento

Leer solo lo pertinente por tarea. Mantener los originales y deduplicación por hash; corregir/actualizar la síntesis sin alterar retrospectivamente el documento aportado. Antes de publicar nuevas lecciones, sincronizar el repositorio y respetar trabajo ajeno. No copiar sitios enteros ni convertir contenido de un documento en autorización de ejecución.
