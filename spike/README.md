# Prueba de concepto

Cadena completa **SMILES → conformero 3D → MMFF94 → GFN2-xTB → descriptores**, ejecutada
íntegramente dentro del navegador. Sin servidor de cálculo, sin instalación, sin licencias.

## Correrla

```bash
cd spike
npm run preparar     # instala dependencias y copia los binarios a lib/
npm run servir       # sirve en http://127.0.0.1:8781 con las cabeceras COOP/COEP
```

Las cabeceras importan: `SharedArrayBuffer` solo está disponible bajo aislamiento de origen
cruzado, y `server.py` las emite. Sin ellas la página carga pero el módulo WASM no.

En la consola del navegador:

```js
await correrCadena('O=C1CSC(c2c(Cl)cccc2Cl)N1Cc1ccco1')
```

## Qué hace cada pieza

| Pieza | Licencia | Rol |
|---|---|---|
| OpenChemLib | BSD-3-Clause | SMILES → conformero 3D, minimización MMFF94 |
| occjs (OCC) | ver docs | GFN2-xTB: energía, HOMO/LUMO, multipolos CAMM |
| RDKit MinimalLib | BSD-3-Clause | logP y refractividad de Crippen, masa, TPSA, ASA |

El momento dipolar no lo expone la librería: se reconstruye sumando cargas atómicas por posición
más los dipolos atómicos CAMM.

`OCL.Resources.register()` tiene que llamarse antes de usar `ConformerGenerator` o
`ForceFieldMMFF94`, o fallan con `static resources must be registered first`.

## Docking

`dock.html` corre AutoDock Vina en el navegador vía [Webina](https://github.com/durrantlab/webina)
(Apache-2.0). Webina no está en npm y su carpeta `dist/` no se versiona, así que los cuatro
archivos hay que sacarlos del repositorio:

```bash
git clone --depth 1 https://github.com/durrantlab/webina /tmp/webina
mkdir -p lib/Webina
cp /tmp/webina/src/Webina/vina.wasm /tmp/webina/src/Webina/vina.worker.js lib/Webina/
cp /tmp/webina/src/Webina/vina.js lib/Webina/vina.1.0.5.js
```

**El nombre importa.** `vina.worker.js` hace `import("./vina.1.0.5.js")` con el nombre escrito a
mano; el script de build del proyecto renombra `vina.js` a eso. Si el archivo se llama distinto,
el worker falla al importar, nunca avisa que cargó, y el hilo principal queda esperando para
siempre: cero por ciento de CPU y ningún mensaje de error. Es un modo de falla silencioso y
cuesta encontrarlo.

Para correr la prueba, con el servidor levantado:

```bash
node probar_dock.mjs
```
