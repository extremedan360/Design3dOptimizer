# Rig de cuadrúpedo y expresiones

## Pivotes y jerarquía

Fijar escala/orientación antes del skin. En el ejemplo: Z arriba y -Y delante; no es obligación del motor. Aplicar transformaciones con cuidado antes de animar y comprobar bind pose.

```text
Root (suelo; desplazamiento global)
└─ Body (masa central)
   ├─ Head (base del cráneo)
   │  └─ Leaf (anclaje del tallo)
   ├─ Bag (sujeción de mochila)
   ├─ Leg_Front_L → Foot_Front_L
   ├─ Leg_Front_R → Foot_Front_R
   ├─ Leg_Back_L → Foot_Back_L
   └─ Leg_Back_R → Foot_Back_R
```

Los huesos pivotan en articulaciones, no simplemente en centros visuales. Comprobar roll/ejes locales al espejar. Dos huesos por pata sirven a un prototipo corto estilizado; saltar/agacharse con anatomía convincente puede requerir más articulaciones y topología.

## Pesos

Los pesos automáticos son inicio, no aprobación. Revisar cuello, axilas, ingles, accesorios y labios. Normalizar por vértice, evitar vértices sin peso y limitar influencias según motor. Uñas/mochila pueden ser rígidas; transiciones blandas requieren mezcla.

Asignar un cuerpo entero a un hueso produce movimiento rígido, no deformación orgánica. Probar cabeza en tres ejes, patas flexionadas y extremas moderadas, sin auto-intersecciones visibles. Para tarjetas: raíz a región anatómica y puntas a guías locales; una guía del lomo no debe arrastrar el hocico por simple cercanía.

## Cara

- Basis neutra: ojos abiertos y boca cerrada. Inicializar explícitamente expresiones a cero; la API/versión puede dar otros valores.
- Blink: párpados cubriendo globo ocular. Aplastar esfera ocular es una aproximación cartoon, no un párpado anatómico.
- OpenMouth: mover labios/mandíbula, con interior/lengua si visibles. Un óvalo exterior animado permite prototipo; no es cavidad oral para diálogo detallado.
- Smile: elevar comisuras, opcionalmente mejillas; probar combinación con boca abierta.

Mantener orden/conteo de vértices de shape keys. No aplicar remesh/decimate sin transferir morphs. Drivers y constraints pueden requerir horneado para exportar.

## Secundarios y comprobaciones

Bag: oscilación amortiguada desde sujeción y prueba de penetración. Leaf: base fija, punta flexible. Fur: pocas guías, raíces fijas y amplitud corta. El ejemplo integra resortes angulares y hornea claves; no contiene solver general de contactos ni física interactiva de motor.

Antes de entregar: suma de pesos cercana a 1, sin vértices sin peso, jerarquía válida, escala/bind pose correctas. Reimportar clips/morphs y observar ojos cerrados, boca abierta, sonrisa y extremos de patas. Un JSON no sustituye mirar la animación.

## Independencia y contrato de los controles

Al consolidar piezas, inicializar cada target completo desde Basis y modificar solo su región. No heredar una mezcla activa; conservar espacio y orden de vértices. Probar 0/0,5/1 y ambos lados, midiendo que los controles declarados independientes no desplazan la región opuesta. Documentar cualquier acoplamiento intencional, en lugar de aceptarlo por accidente. Los nombres anatómicos o grupos de región ayudan a localizar fallos, pero no demuestran independencia por sí solos.

Validar cierre con poses y extremos reales de mirada, además de neutral. Si el contrato exige globo presente y sin retracción, comprobar que no se oculta ni encoge para simular la cobertura. Otros estilos pueden usar retracción explícita y horneada; no mezclar sus criterios. Clasificar primer impacto de rayos como párpado, cuerpo, globo visible o fallo, y distinguir caras traseras. El cuerpo puede ocluir de forma legítima; los rayos solo complementan renders de vistas pertinentes y mezclas parciales.

Separar huesos deformantes exportados de controles IK/autoría, hornear dependencias y reimportar. Revisar deformación y apoyos en muestras temporales; una cuenta de huesos o cinco poses finitas no prueban contacto continuo. Exportar cada estado lógico con cuerpo y cara sincronizados, no como pistas sueltas por familia de objetos. Ver la [revisión de rig independiente y modular](../../../../docs/reviews/cuy-rig-independiente-y-modular.md) para evidencia y límites.
