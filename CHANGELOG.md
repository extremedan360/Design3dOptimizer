# Cambios

## 2026-11-13

- Aprendizajes generalizados de rig independiente: 31 huesos de deformación y seis clips de tres segundos, sin copiar assets o fotografías de otro proyecto.
- Inventario modular de Blender para registrar objetos, jerarquía, morphs y armatures; no certifica por sí solo independencia funcional.
- Nueva inferencia StableGen real en cinco etapas (512, INT8/MPS), reparación unsigned con fallos conservados y ensamble estático exploratorio de 16.952 triángulos con accesorios separados en Blender. Revisión exploratoria Blender/GLB aprobada con límites: 18 mallas, siete materiales, cero imágenes, 421.076 bytes y cinco tubos abiertos de accesorios pendientes. No incluye rig, nuevas animaciones ni FPS móviles.
- Runner parametrizado y adaptador de checkpoints; la preparación produjo la misma firma que la inferencia original, sin afirmar una segunda ejecución completa.

## 2026-11-12

- Habilidad portable para recursos de videojuegos: modelado, vegetación/estructuras, seres vivos, pelaje, rig, animación y VFX.
- Tres bibliotecas aportadas, deduplicación por SHA-256 y análisis crítico de versiones/alcance.
- Revisión de cuatro videos y de DESIGN:OS 3D Blender, sin copiar su implementación.
- Ejemplo reproducible de cuy con dos representaciones de pelo, rig, expresiones y resortes horneados.
- Inspección de GLB, inventario de Blender, runner acotado y pruebas de reimportación.

- Paleta runtime del cuy: materiales 13→4 y grupos 15→7, sin quitar huesos o expresiones. Selección auto/CPU/CUDA para no imponer NVIDIA.
- Instalación global con biblioteca compartida configurable y mantenimiento de aprendizajes generales, sin mezclar archivos privados de otros proyectos.
