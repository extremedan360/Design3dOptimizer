# StableGen por etapas y preparación modular

Ensayo local de generación geométrica desde una referencia privada, con el constructor de grafo StableGen (`68f2d165fdcdead669d322a86e6dc39887381354`), ComfyUI (`426f5eea52a7ece1dd599fff4cb6cd1f352ddd24`) y TRELLIS.2 INT8 en Apple Silicon de 18 GiB. Resolución 512, 12 pasos, semilla 13112026, sin generación de texturas. No es una prueba de todos los paneles del addon StableGen.

Las cinco fases usan servidores secuenciales y checkpoints locales: condicionamiento de imagen, estructura, preparación de forma, muestreo de forma y decodificación/exportación. Se detiene exclusivamente el servidor iniciado por el runner. El puerto 8190 debe estar libre; el runner rechaza un servicio existente. Conserva cada fase, su firma y el registro de memoria. La firma comprende referencia, constructor de grafo, adaptador y grafos resultantes. No se deben mezclar checkpoints de otros ensayos.

## Entorno previo

No se descargan modelos ni se instala software automáticamente. Hace falta un clon compatible de StableGen, ComfyUI con sus nodos TRELLIS.2 y pesos `trellis_2_int8_convrot.safetensors` y las dependencias de ese flujo ya configurados. El Python de ejecución necesita `requests` y `psutil`; ComfyUI necesita sus dependencias, incluyendo Torch y safetensors. Revisar licencias upstream y de los pesos por separado.

El adaptador local original está en `checkpoint_nodes/__init__.py`. Para una instalación aislada de ComfyUI, copiar **esa carpeta** a `custom_nodes/cuy_checkpoints/` sin sobrescribir otra versión. No es código upstream StableGen: serializa tensores y metadatos mediante safetensors, sin pickle de objetos arbitrarios. No cargar checkpoints no confiables.

```sh
python run_stages.py --comfy /ruta/ComfyUI --stablegen /ruta/stablegen --comfy-python /ruta/ComfyUI/.venv/bin/python --reference /ruta/referencia.jpg --output /ruta/ensayo-nuevo --prepare-only
```

Ejecutar desde esta carpeta y con el Python del entorno adecuado. `--prepare-only` escribe los grafos sin iniciar inferencia. Quitar esa opción ejecuta las cinco etapas; no ejecutar simultáneamente con un motor o render pesado. El runner usa entrada/salida y caché propias dentro del destino. El nombre interno de la entrada termina en `.jpg`; usar una referencia JPEG.

Se observaron cinco fases completadas en el ensayo original. Esta versión parametrizada pasó preparación y produjo **la misma firma de referencia/grafos/adaptador** que la ejecución completa original; no se presenta como una segunda inferencia completa. Los guardas muestrean cada 15 segundos y pueden perder picos; interrumpen si el swap adicional supera 4 GiB en una fase, o hay menos de 0,8 GiB disponibles junto con más de 2 GiB de swap adicional. No son una reserva de memoria ni garantía para otro equipo.

## Alcance

La generación inicial no crea mochila, ojos o esqueleto independientes automáticamente. Puede fusionar complementos, inventar suelo o producir superficies perforadas. Conservar la salida original, revisar el cuerpo sin complementos, reparar y después modelar cada accesorio como objeto separado, con pivote y sujeción. No atribuir esa reconstrucción manual a la IA.

Consultar [lecciones y evidencia](../../docs/reviews/cuy-rig-independiente-y-modular.md) y [reparación de superficies](../../docs/reviews/reparacion-superficie-generada.md). El inventario por objeto se obtiene con [modular_report.py](../../scripts/modular_report.py); no certifica por sí solo que una mochila esté separada semánticamente del cuerpo.

Los modelos, referencia privada, pesos, latentes y cachés no forman parte de este repositorio. Los artefactos completos se conservan en la entrega local autorizada.

## Ensamblar este ejemplo después de reparar la base

`assemble_modules.py` recibe el Blend de una **única malla de cuerpo ya reparada**, con transformación aplicada, Z arriba y frente -Y. Sus medidas, máscaras de color y colocación son las del cuy de este ensayo; no adaptan automáticamente otro animal. Conservar la base antes de ejecutarlo. Escribe sólo en el destino indicado, que debe ser una carpeta nueva para no sobrescribir ediciones manuales.

```sh
blender --background --factory-startup --threads 4 --python-exit-code 2 --python assemble_modules.py -- --body /ruta/cuerpo-ia-base.blend --output /ruta/ensamblaje
```

La geometría del cuerpo procede de la nueva ejecución StableGen y una reconstrucción posterior. La mochila, bolsillos, solapa, correas, hebilla, asa, ojos, nariz y brote son modelados separados en Blender. El script exporta conjunto, cuerpo, mochila y brote en GLB, un Blend editable y tres vistas. Los colores del cuerpo se interpolan por vértices; no son texturas generadas por IA. Las correas se aproximan a la superficie real mediante rayos y aún necesitan revisión de contactos al animar.

Esta versión es estática: no incluye el rig ni los seis clips de otra prueba. No hereda esas comprobaciones. Tampoco certifica fidelidad exacta, retopología facial final ni rendimiento móvil. El informe `assembly-manifest.json` identifica piezas, triángulos y procedencia; complementar con reimportación e inventario por objeto.

## Reparar y revisar la base antes del ensamblaje

Los cuatro scripts siguientes son variantes portables de los scripts de trabajo ejecutados en este ensayo. Pasaron compilación sintáctica y `--help`; **no se ha repetido toda la reparación con estas variantes parametrizadas**. La inferencia y la reparación originales sí se ejecutaron. No interpretar esa comprobación de interfaz como otra generación ni una reproducción numéricamente idéntica.

Ejecutar estos comandos desde esta carpeta, reemplazando los destinos externos. Usar Blender con NumPy para las etapas Blender; el Python de `unsigned_repair.py` necesita NumPy, SciPy y scikit-image (en el ensayo, scikit-image 0.25.2 en una carpeta aislada). No hace falta cargar ComfyUI para reparar. Ningún comando instala dependencias. Conservar cada checkpoint y observar frente, perfil, espalda y coronilla antes de continuar.

```sh
blender --background --factory-startup --threads 4 --python-exit-code 2 --python floor_only.py -- --source /ruta/generado.glb --outputfolder /ruta/postfloor --floor-z -0.1711883544921875 --floor-band 0.00018

python unsigned_repair.py --source /ruta/postfloor/postfloor.glb --outputfolder /ruta/unsigned --resolution 256 --padding 6 --closing-sizes 9 13 --min-solid-voxels 1800000 --component-policy largest --repair-config case.json --sigma 0.6 --isovalue 0.501 --threads 4

blender --background --factory-startup --threads 4 --python-exit-code 2 --python render_unsigned.py -- --input /ruta/unsigned/surface.npz --outputfolder /ruta/review --object-name Cuerpo_StableGen_unsigned --prefix body-surface --neck-y-min -0.16 --neck-y-max -0.08 --feet-z-max -0.12 --protect-config case.json --torso-relax-weight 0.20 --smooth-iterations 12 --smooth-factor 0.75 --render

blender --background --factory-startup --threads 4 --python-exit-code 2 --python finalize_body.py -- --input /ruta/review/body-surface.blend --outputfolder /ruta/body --object Cuerpo_StableGen_unsigned --object-name Cuerpo_StableGen_Base --prefix cuerpo-ia-base --target-triangles 18000 --render

blender --background --factory-startup --threads 4 --python-exit-code 2 --python assemble_modules.py -- --body /ruta/body/cuerpo-ia-base.blend --output /ruta/ensamblaje
```

`case.json` conserva las coordenadas y protecciones del último ensayo de reparación: Blender Z arriba, frente -Y, fuente RAW SHA-256 `12f0a0356a7887a2708224bae374fb7593e7ca5a0c96f529cb43ac97348510b4`. Sus umbrales y envolvente son específicos de esa fuente y escala. Para otro modelo hay que medirlos; no son parámetros universales ni detección automática de accesorios. La región dorsal se reconstruye manualmente como **volumen**, protegiendo orejas y conservando la zona anterior e inferior. El suavizado geométrico reduce el escalón de unión y protege orejas y plantas.

`floor_only.py` conserva coordenadas de los vértices retenidos, pero su salida es geométrica: no conserva UV ni materiales originales. `unsigned_repair.py` rasteriza superficies sin depender de su signo, prueba cierres y rellena el interior antes de extraer la superficie. El número de vóxeles sólo ayuda a detectar una cáscara; no valida anatomía. El cierre de 9 fue insuficiente en este caso y se usó 13; un parche limitado a una tapa superior también fue rechazado. Los booleanos sobre la sopa de triángulos habían destruido el cuerpo y se descartaron.

`finalize_body.py` reduce geometría con un objetivo explícito y exige una malla cerrada por defecto; `--allow-open` es únicamente diagnóstico. La base de trabajo aprobada para avanzar tuvo 18.000 triángulos, antes de los ajustes del ensamblador. Esas cifras no describen automáticamente el conjunto ensamblado ni garantizan rendimiento móvil. Estos pasos no añaden rig ni animaciones.
