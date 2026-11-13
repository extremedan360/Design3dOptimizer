# Biblioteca compartida entre proyectos

La habilidad puede instalarse para el usuario, mientras un clon estable de Design3dOptimizer conserva documentación, originales, herramientas y aprendizajes. No necesita duplicarse la biblioteca en cada juego.

## Localizar y consultar

Leer `local-library.json` en la raíz de la habilidad instalada si existe. Campos:

```json
{
  "repository_path": "ruta absoluta al clon compartido",
  "repository_url": "https://github.com/extremedan360/Design3dOptimizer.git",
  "optimization_first": true,
  "sync_before_relevant_task": true,
  "learning_mode": "local-notes",
  "publication_scope": "generalizable-knowledge-only"
}
```

Es configuración personal: no copiarla a Git ni sustituir la ruta por una del proyecto actual. Confirmar que el clon/remoto coinciden antes de escribir. Si no existe configuración, usar las referencias incluidas y el repositorio conocido; no inventar una ruta o autorización.

Al iniciar trabajo relevante de recursos 3D, revisar estado y sincronizar el clon con fetch/pull --ff-only cuando esté habilitado y sea posible. Preservar cambios locales. Red o permisos no disponibles: consultar la copia local, indicar su revisión y continuar el trabajo que no dependa de cambios nuevos.

Elegir la lectura mínima: `docs/library/README.md`, el capítulo pertinente de la habilidad y las guías originales relacionadas. Consultar `docs/library/ANALISIS.md` para versiones y limitaciones. No cargar todos los manuales cada turno.

## Registrar aprendizajes

Al terminar un experimento que aporte algo generalizable, seguir `aprendizaje.md`: problema, versión, método, medida, resultado y límite. Primero completar la tarea del usuario; después actualizar la guía o ejemplo adecuado. Registrar un lote de lecciones útiles, no un commit por cada ajuste de parámetro.

- `local-notes`: preparar conocimiento local; publicar solo cuando haya autorización.
- `publish-general-lessons`: preferencia de mantenimiento expresamente habilitada por el usuario. Publicar lecciones generales dentro de esa autorización, con revisión, pruebas pertinentes, commit breve/descriptivo y verificación remota. Respetar restricciones superiores, permisos disponibles y privacidad del proyecto de origen.

No publicar modelos, diseños privados, nombres de clientes, credenciales, conversaciones o datos del proyecto por estar aprendiendo de él. Si una lección no puede generalizarse sin revelar información privada, conservarla en el proyecto autorizado y explicar el límite.

Antes de publicar: fetch/pull, revisión del diff, comprobaciones y commit; consultar remoto otra vez y push sin forzar. Divergencia o conflicto requiere preservar y revisar ambas versiones. Informar el SHA publicado. No ejecutar tareas en segundo plano ni prometer observar otros chats.

## Mantener la instalación

Un pull del clon actualiza la biblioteca; no cambia automáticamente la copia global de la habilidad. Si cambian sus instrucciones, comparar fuente e instalación y actualizar solo los archivos de la habilidad, preservando `local-library.json` y modificaciones personales. Verificar referencias y metadatos después. La disponibilidad depende de la carga de habilidades de la sesión; puede invocarse por nombre.
