# Contribuir

1. Revisar estado y diff. Ejecutar fetch/pull --ff-only preservando trabajo local.
2. Actualizar la guía existente; enlazar en lugar de duplicar contenido.
3. Clasificar evidencia: probado, fuente primaria, inferencia o pendiente. Indicar fecha, versión y límites.
4. Ejecutar scripts modificados y comprobar artefactos. Las comprobaciones estructurales no prueban un juego.
5. Revisar tamaño/licencias; excluir modelos de IA, cachés y datos privados.
6. Commit con asunto breve como `docs(pelaje): explicar coste del alpha recortado` y cuerpo con cambios y pruebas reales. Consultar remoto antes del push, integrar avances sin sobrescribir y verificar SHA.

Una corrección actualiza resultados sin borrar el fallo que explica la decisión. Las comparaciones requieren condiciones similares o explicar sus diferencias. Actualizar el repositorio no instala la habilidad en copias ajenas: cada usuario sincroniza/copia deliberadamente.

Comprobaciones locales sin Blender:

```sh
python scripts/check_repository.py
python -m unittest discover -s tests -v
```

Los cambios en generación o rig necesitan además ejecutar las etapas afectadas y `examples/cuy/verify.py` sobre el GLB realmente exportado. No publicar un reporte anterior como validación de una versión nueva.
