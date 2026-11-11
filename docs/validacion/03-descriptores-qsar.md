# Paso 3 — Descriptores (C2) y QSAR del TP 1 (C3)

**Fecha:** 2026-11-10. **QuEtool:** commit `ff964ce`, corrida real de la app publicada
(servida localmente desde el mismo árbol) en Edge headless, manejada por CDP con el driver
`arnes/c2-app.mjs`. **Referente:** RDKit de línea de comandos 2026.09.1 (el que fija el
protocolo 00). **Estadística:** scipy 1.16.3, pruebas de Fisher y Student a α = 0,05.

## C2 — Descriptores

### Qué se hizo

La app calcula por ligando: masa, clogP, refractividad (MR), TPSA y superficie (ASA de
Labute) con RDKit (build JavaScript), y dipolo, HOMO, LUMO y gap con GFN2-xTB (occjs)
sobre la geometría MMFF94 del confórmero. El protocolo pide dos cosas: que los
descriptores que RDKit también calcula **coincidan salvo redondeo** con el referente de
línea de comandos, y que los que dependen de la geometría salgan de un **SCF convergido**.

Se generaron los SMILES canónicos de los once ligandos desde los SDF de materiales con el
RDKit CLI (el referente no produce lo que se valida: sólo las entradas), y la app real los
corrió uno por uno. Resultados crudos: `datos/descriptores_quetool_nnrti.json` (salida de
la app) y `datos/descriptores_nnrti_comparacion.json` (comparación).

### Resultado

SCF de GFN2 convergido: **11/11**. Desviación máxima app vs RDKit CLI (los cinco
descriptores topológicos):

| Descriptor | max\|Δ\| |
|---|---:|
| masa | 0,005 |
| clogP | 0,000 |
| MR | 0,005 |
| TPSA | 0,040 |
| ASA | 0,044 |

Todas las diferencias son redondeo de visualización de la app (2–3 decimales). Los valores
son idénticos al referente; la verificación química también cierra (EFZ: masa 315,68,
clogP 4,073; EFZ-Br: clogP 4,182 — la pareja del compuesto de diseño).

**C2: ACEPTA.** Con la brecha ya declarada en el protocolo y en
`consignas-tp-literal.md`: QuEtool no calcula Volume, Polarizability ni Hydration Energy,
que la guía pide en HyperChem. No es una falla de este paso: es una brecha de cobertura
conocida, registrada aparte.

## C3 — QSAR del TP 1

### Parte B — los diez NNRTI, pIC50 = a·d + b (un descriptor por vez)

| Descriptor | R² | r | p | significativo (0,05) |
|---|---:|---:|---:|---|
| clogP | 0,782 | 0,884 | 0,0007 | **sí** |
| TPSA | 0,428 | −0,654 | 0,040 | **sí** |
| MR | 0,075 | 0,273 | 0,445 | no |
| HOMO | 0,091 | 0,301 | 0,398 | no |
| ASA | 0,025 | 0,158 | 0,664 | no |
| masa | 0,013 | 0,115 | 0,751 | no |
| gap | 0,014 | −0,118 | 0,746 | no |
| LUMO | 0,012 | 0,112 | 0,759 | no |
| dipolo | 0,006 | 0,080 | 0,827 | no |

**Mejor modelo de dos variables:** `pIC50 = 5,088 − 0,0055·masa + 1,145·clogP`,
R² = 0,839, R²aj = 0,793, **F = 18,20 (p = 0,0017)**. El coeficiente de masa no es
significativo (t = −1,57, p = 0,16) y el de clogP sí (t = 5,98, p = 0,0006): caso de libro
de multicolinealidad — masa y lipofilia crecen juntas en esta serie. La matriz de
ortogonalidad lo confirma (masa–ASA r = 0,937; dipolo–masa r = 0,872; TPSA–clogP
r = −0,753), que es exactamente el análisis que el TP manda hacer antes de combinar.

### Parte A — las 15 TZD de Rawal 2005

Con los descriptores **publicados** en la guía (logP, μ(MNDO), Eoop):

| Modelo | R² | F | p | significativo |
|---|---:|---:|---:|---|
| pEC50 ~ logP | 0,342 | — | 0,022 | sí |
| pEC50 ~ μ | 0,106 | — | 0,237 | no |
| pEC50 ~ Eoop | 0,014 | — | 0,674 | no |
| pEC50 ~ logP + μ | 0,482 | 5,59 | 0,019 | sí |
| pEC50 ~ logP + Eoop | 0,416 | 4,27 | 0,040 | sí |
| pEC50 ~ μ + Eoop | 0,242 | 1,91 | 0,190 | no |
| pEC50 ~ logP + μ + Eoop | 0,880 | 26,92 | < 0,001 | sí |

Ortogonalidad: r(logP, μ) = −0,082 · r(logP, Eoop) = −0,247 · **r(μ, Eoop) = −0,569**.
Esa última correlación es artificial: viene de los valores transpuestos del compuesto 11
(μ = 0,012 y Eoop = 4,189 en la tabla publicada). Con los descriptores de QuEtool
(clogP: R² = 0,317, p = 0,029; clogP + dipolo: R² = 0,650, F = 11,13, p = 0,0018) la
anomalía salta sola: QuEtool le da al compuesto 11 un dipolo de **5,68 D**, el mayor de la
serie, y no 0,012 — exactamente lo que anticipaba `referencia-tp-qsar-docking.md`.

**C3: ACEPTA.** Se pudieron ajustar y comparar todos los modelos de una y dos (y tres)
variables con R², Fisher y Student a α = 0,05, y aplicar el criterio de ortogonalidad; los
números crudos están en `datos/resultados_c3.txt` y el script en `arnes/c3-qsar.py`.
