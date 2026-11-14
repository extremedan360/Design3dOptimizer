# Métricas conjuntas de normales

Utilidad original de biblioteca estándar de Python 3.12, bajo la licencia MIT del repositorio. No requiere Blender ni un motor. Mide vectores correspondientes; el llamador debe demostrar antes la correspondencia de esquinas y topología.

Desde esta carpeta:

```sh
python -B -m unittest discover -s . -p test_normal_metrics.py -v
```

Las cuatro pruebas son sintéticas: ángulos pequeños y opuestos, límites conjuntos, error de magnitud e entradas inválidas. No validan un recurso externo.

```python
from normal_metrics import compare_normals

metrics = compare_normals([(0, 0, 1)], [(0, 0, 1)])
assert metrics["exactComponentCount"] == 1
assert metrics["passed"] is None  # No se proporcionaron límites.
```

`exactComponentCount` cuenta igualdad numérica de componentes; no inspecciona patrones binarios o codificaciones internas. Los límites opcionales los aporta el llamador después de medir su caso. El helper no normaliza en silencio para medir componente/longitud, no corrige vectores ni lee archivos del motor. Normaliza copias exclusivamente para medir ángulos con `atan2`.

Consultar la [guía de UV, materiales y normales](../../docs/reviews/uv-materiales-normales.md) para la separación entre integridad del editable, revisión visual y pruebas en motor. No hay tolerancias universales, promesa de rendimiento o recursos privados incluidos.
