# Aplicación

Una sola página, sin instalación. Las librerías se bajan de jsDelivr, así que alcanza con
servir `index.html` desde cualquier servidor estático.

## Abrirla

**Publicada en GitHub Pages.** En el repositorio, Settings → Pages → Source: `main`, carpeta
raíz. Queda en `https://dimacio.github.io/modelado_online/app/`.

**O localmente**, con `servir.bat` (doble clic) o:

```bash
python3 servidor.py 8000
```

`servidor.py` no es `python -m http.server`: además emite las cabeceras COOP y COEP, que son las
que habilitan `SharedArrayBuffer`. Sin ellas AutoDock Vina no arranca. Los descriptores funcionan
igual con o sin cabeceras, y por eso la página también anda en GitHub Pages.

No alcanza con hacer doble clic en el archivo: abierto como `file://` el navegador bloquea la
carga de módulos.

## Qué hace

SMILES → confórmero 3D → MMFF94 → GFN2-xTB → descriptores, todo en la pestaña. Cada cálculo se
acumula en una tabla que se exporta como CSV.

Incluye un editor de estructuras 2D (OpenChemLib) conectado al campo de SMILES en los dos
sentidos.

## Estado del docking

Vina ya corre en el navegador y la pestaña tiene la caja de docking real, pero falta un paso:
convertir el ligando dibujado a PDBQT. OpenBabel compilado a WebAssembly ejecuta su `main()` al
iniciar y se queda leyendo stdin, lo que bloquea el hilo principal de la página. Hay que aislarlo
en un iframe y hablarle por `postMessage`, que es exactamente lo que hace Webina con su
PDBQTConvert. Eso además mantiene separada la licencia GPL de OpenBabel del resto del código.
