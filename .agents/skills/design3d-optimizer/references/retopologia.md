# Retopología, decimación y LOD

Decimación reduce geometría; retopología reorganiza para uso, UV y deformación. Pocas caras no garantizan buen flujo para animación.

- Collapse: útil en copias estáticas/LOD; evaluar contorno, UV, normales y articulaciones, no solo porcentaje.
- Un-Subdivide: intenta retirar subdivisión regular; funciona sobre patrones adecuados, no deshace perfectamente cualquier historial. Revisar después de cada incremento.
- Planar/Dissolve: superficies casi coplanares; menos general para anatomía curva.
- Manual/asistida: bucles en boca, ojos y articulaciones; transferir detalle por bake con cage/distancia comprobados.

Conservar high poly/materiales. Al cambiar topología, transferir o rehacer UV y hornear color/normal/rugosidad necesarios. IA no garantiza pesos, morphs o texturas conservados.

LOD0 cercano; LOD1 menos geometría/tarjetas; LOD2 puede depender solo del material. Evaluar por tamaño en pantalla. Planear también sombras, física y skin. Tres archivos no implementan selección automática en motor.

Una malla generada con paredes dobles o winding incoherente puede necesitar reconstrucción de volumen antes de QEM. Ocupación sin signo, cierre morfológico y marching cubes funcionaron en un ensayo documentado; pueden borrar dedos/cavidades y accesorios separados. Inspeccionar componentes y silueta antes de QuadriFlow. Cerrar solo huecos medidos y justificados: manifold no significa buen flujo facial. Ver [reparación de superficies generadas](https://github.com/extremedan360/Design3dOptimizer/blob/main/docs/reviews/reparacion-superficie-generada.md).

## Lectura crítica

Una reducción «sin pérdida» de un tutorial es un resultado de ese caso. Decenas de miles de caras no implican automáticamente media hora extra de render ni RAM agotada. El tutorial Hunyuan termina con pérdida de detalles/materiales y deja la recuperación para otro video: no demuestra todo el pipeline.
