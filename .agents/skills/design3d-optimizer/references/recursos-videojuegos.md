# Recursos 3D para videojuegos en general

Seleccionar técnicas por cámara, plataforma, cantidad visible, interacción y presupuesto medido. La optimización se aplica a memoria, tiempo CPU/GPU, cobertura de pantalla, cargas, materiales y mantenimiento, no solo a caras.

## Vegetación y terreno

Árboles: geometría para tronco y ramas que alteren silueta; agrupar hojas en tarjetas/clusters o mallas simples según plano de cámara. Compartir atlas/materiales cuando sea útil. Medir alpha, doble cara, sombras y viento: una hoja de dos triángulos puede costar más píxeles que un tronco opaco.

Hierba: agrupar instancias y limitar distancia/densidad; variar escala/orientación con semilla estable. Viento mediante máscaras por vértice para fijar raíces y mover puntas. Simular o colisionar cada brizna rara vez es el primer paso; reservar interacción localizada donde se vea. Medir el método de instancing realmente soportado por el motor/pipeline.

LOD: reducir hojas/ramas/alpha y sombras a distancia; considerar impostores con transiciones comprobadas. Un billboard no mantiene volumen desde todas las vistas. Evitar reflejar texturas o billboards que revelen una iluminación incoherente.

Terreno: dividir en sectores para streaming/culling; controlar densidad por pendiente/silueta y costo de capas del shader. No hornear todo el mundo en un único objeto. Colisiones de suelo y visual pueden tener resoluciones diferentes, probadas con el controlador del jugador.

Prueba: cámara rasante entre vegetación, iluminación de día/noche, ráfaga de viento y escena con cantidades reales. Registrar overdraw y picos al cargar, no solo un árbol aislado.

## Estructuras, edificios y escenarios

Planear módulos, escala y retícula. Reutilizar geometría/materiales sin repetir costuras visibles o destruir variedad. UV/trim sheets/tileables pueden ahorrar textura; verificar densidad de texel y bordes. Añadir bisel donde mejore reflejo/silueta, no en toda arista por costumbre.

Separar módulos para culling, puertas y destrucción. Combinar mallas solo tras medir materiales/draw calls y efecto sobre visibilidad y memoria. Preparar UV de iluminación si el pipeline usa lightmaps; no confundir UV de material con requisitos de iluminación horneada.

Colliders primitivos/compuestos para paredes/suelos simples; proxies de colisión separados de adornos. Pasos, puertas y escaleras deben probarse con dimensiones del jugador. Un edificio visual no demuestra navegación o colisiones correctas.

Prueba: escala interior, recorrido del jugador, luz/sombras, uniones, puertas en extremos y streaming/culling. Para partes móviles comprobar toda la trayectoria, no solo endpoints.

## Objetos, vehículos y mecanismos

Pivotes y sockets son parte del diseño: puerta en bisagra, rueda en eje, herramienta en punto de agarre. Separar piezas que deban articularse y documentar orientación. Componentes repetidos pueden compartir malla; colores/variantes deben medirse para no multiplicar materiales innecesarios.

Vehículos: separar visual, colisión y simulación. Un modelo con ruedas no constituye un vehículo funcional. Usar proxies físicos simples y probar estabilidad en el motor. Reservar destrucción y fragmentos para el alcance real; retirar fragmentos fuera de vista o después de un tiempo.

## Seres vivos

Definir anatomía y acciones: cuadrúpedo, bípedo, ave, pez, insecto o planta animada. No imponer un rig humanoide a todos. Colocar articulaciones donde se deforman, preparar loops/volumen y probar poses. Pelo/plumas/escamas requieren representaciones distintas por tamaño en pantalla.

Separar física de gameplay de movimiento secundario. Cuerpo/collider principal gobierna contactos del juego; orejas, cola, hojas o mochila pueden usar guías simplificadas. Probar clipping y teletransporte/reaparición. Reducir skin, expresiones y secundarios lejanos cuando no aporten imagen.

## Efectos visuales

Humo, fuego, polvo, agua, magia, impactos y clima pueden usar partículas, flipbooks, mallas, shaders o simulación según necesidad. Distinguir una simulación de autoría horneada en textura de una simulación ejecutada en juego.

Presupuestar área de pantalla y capas transparentes, luces y sombras de cada efecto. Limitar spawn, duración, colisiones e interacciones; reutilizar objetos cuando la plataforma lo justifique. Definir bounds/culling para que no desaparezcan efectos visibles ni se procesen emisores lejanos.

Un flipbook pequeño con mipmaps puede ser más útil que una simulación volumétrica completa, pero la compresión y el blending pueden crear bordes. Revisar fondos claros/oscuros, cámara cercana y múltiples efectos simultáneos. No dar por resuelto el coste por usar pocos polígonos.

## Entrega por categoría

Conservar editable, dependencias, parámetros, procedencia y exportación. Añadir pruebas pertinentes: un prop estático no necesita Animator; un efecto no necesita topología manifold salvo una razón concreta; un personaje no necesita requisitos de fabricación por defecto. Marcar explícitamente lo que no se probó en motor.
