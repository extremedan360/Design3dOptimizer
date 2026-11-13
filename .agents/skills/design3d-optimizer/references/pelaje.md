# Pelaje optimizado

| Técnica | Aporta | Coste/límite |
| --- | --- | --- |
| Normales/rugosidad | Microdetalle interior | No rompe contorno |
| Hair cards | Mechones en planos texturizados | Geometría, descarte de píxeles, peinado y atlas |
| Shells | Volumen con capas | Multiplica superficies y overdraw |
| Shells + fins | Mejor contorno | Geometría adicional y posible dependencia de cámara |
| Parallax occlusion | Profundidad aparente | Varias muestras por píxel; contorno delicado |
| Curvas/hebras | Fibras y primer plano | Densidad/sombreado/sombras; sin pelo estándar GLB |

Para pelo corto, comenzar con base y tarjetas; usar curvas como referencia de presentación. Comparar cobertura en pantalla y animales simultáneos. Un buen render offline no demuestra que una melena funcione a tiempo real en móviles.

Distribuir raíces por área de triángulos, con normales suaves. Excluir zonas ocultas, ojos, labios e interior de orejas. Peinar coherentemente; variar longitudes/anchos y compartir atlas. Transferir normales de superficie puede evitar aspecto de láminas duras. Verificar luz posterior y bordes.

Alpha recortado evita mezcla gradual, pero aún paga píxeles descartados, superficies a doble cara, sombras y mipmaps. Las fibras finas pueden desaparecer a distancia. Reducir tarjetas y simulación por tamaño en pantalla; exportar LOD no implementa su selección en motor.

## Movimiento

Separar raíz, guías y mechones visibles. Pocas guías/huesos pueden mover muchos pelos; raíz fija y mayor peso hacia punta. Pelaje corto necesita poca amplitud.

```text
velocidad += (fuerza - rigidez*angulo - amortiguacion*velocidad) * dt
angulo += velocidad * dt
```

Usar subpasos acotados y parámetros por accesorio. Limitar ángulos no resuelve colisiones. Una simulación horneada reproduce el movimiento calculado; responder a viento/contacto durante partida exige integración del motor y pruebas allí. Reiniciar estados en teletransporte/reaparición.

En el ejemplo se compararon 2.200 tarjetas y 35.000/70.000 curvas de cuatro puntos. No llamar triángulos a puntos de curvas ni mostrar la versión de hebras como si fuera el GLB de tarjetas.
