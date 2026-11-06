# Aplicación

Una sola página, sin instalación. Las librerías se bajan de jsDelivr, así que alcanza con
servir `index.html` desde cualquier servidor estático.

## Abrirla

**Publicada en GitHub Pages.** En el repositorio, Settings → Pages → Source: `main`, carpeta
raíz. Queda en `https://dimacio.github.io/modelado_online/app/`.

**O localmente.** Desde esta carpeta:

```bash
python3 -m http.server 8000
```

Ese comando levanta un servidor web que publica los archivos de la carpeta actual en el
puerto 8000. Después se abre `http://localhost:8000` en el navegador. Para cortarlo, Ctrl+C.

No alcanza con hacer doble clic en el archivo: abierto como `file://` el navegador bloquea la
carga de módulos.

## Qué hace

SMILES → confórmero 3D → MMFF94 → GFN2-xTB → descriptores, todo en la pestaña. Cada cálculo se
acumula en una tabla que se exporta como CSV.

No necesita las cabeceras COOP/COEP, por eso anda en GitHub Pages. El docking sí las necesita,
porque Vina usa `SharedArrayBuffer`; esa parte va a requerir otro hospedaje o un service worker
que las inyecte.
