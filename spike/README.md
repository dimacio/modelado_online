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
