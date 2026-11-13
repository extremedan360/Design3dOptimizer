# Automatización de animación con Blender Python y agentes MCP

## Qué puede automatizarse
- Validación de nombres, armatures, acciones, frames y rutas.
- Exportación por lotes de clips FBX.
- Detección de acciones sin keyframes, objetos sin rig y nombres duplicados.
- Generación de reportes de auditoría JSON/CSV.

## Qué necesita inspección humana
- Calidad del movimiento, contacto de pies, clipping, deformación, acting y respuesta al input.
- Un script no garantiza calidad cinematográfica ni compatibilidad total de rigs.

## Contrato recomendado para el agente
Entrada: descripción del personaje, motor y versión, plataforma objetivo, lista de animaciones, rig requerido y FPS.
Salida: `.blend` editable, FBX, listado de clips, documentación de escala/ejes, reporte de validación y escena de prueba en Unity.

## Pruebas de aceptación
- Importa sin errores.
- Avatar válido.
- Cada clip se reproduce y puede repetirse cuando corresponde.
- No hay desplazamientos o escalas inesperados.
- Transiciones de Animator probadas en Play Mode.
- Rendimiento medido en escena representativa.

API: https://docs.blender.org/api/current/
