# Consignas del TP, al pie de la letra

> Extraído de los originales el 2026-11-10: `Guía del TP.pdf` (QSAR, Partes A y B),
> `TP2-Docking-2026.docx` y `TP2-Docking-2026-Add.docx` (anexo). Es una lista de lo que
> el TP pide, no una interpretación. Sirve para contrastar, consigna por consigna, qué
> cubre QuEtool.

## Aviso importante: son dos series de compuestos distintas

Esto no estaba claro en el resumen anterior y cambia qué hay que validar.

**Parte A — las 15 tiazolidin-4-onas de Rawal 2005.** La guía **da** la tabla de
descriptores (logP, μ(MNDO), E_oop) junto a las EC₅₀. No se modela nada: es un ejercicio
de estadística sobre números publicados. QuEtool no interviene.

**Parte B — los 10 NNRTI reales.** Ésta es la serie que se modela de verdad:

| Ligando | PDB | IC₅₀ (nM) |
|---|---|---|
| GFA | 3DLE | 2.00 |
| EFV (EFZ) | 1FK9 | 6.03 |
| TBO | — | 14.13 |
| TNK | 1RT2 | 40.74 |
| NVP | 3HVT | 89.13 |
| HBQ | 2OPP | 177.83 |
| QNO47b | — | 213.80 |
| U05 | 1RTH | 398.11 |
| ZZE | 2WON | 630.96 |
| QNO47c | — | 912.01 |

Estos son los que se modelan en TP 1, se les calculan descriptores, se usan para el QSAR
y se dockean en TP 2. **La réplica del TP es sobre estos diez, no sobre las TZDs.**

## TP 1 / Parte B — descriptores que pide la guía

Por cada uno de los 10 ligandos, con HyperChem:

| Descriptor | Cómo lo pide la guía |
|---|---|
| SA (Å²) | QSAR properties |
| SA-grid (Å²) | *Solvent accessible surface*, probe 1.4 Å, *Points On Cube Side* = 50 |
| Volume (Å³) | QSAR properties, mismas opciones |
| Hydration Energy (kcal/mol) | QSAR properties |
| logP | QSAR properties |
| RM (Å³) | refractividad, QSAR properties |
| Polarizability (Å³) | QSAR properties |
| PM | QSAR properties |
| Momento dipolar | *single point* AM1 sobre la estructura optimizada |
| HOMO, LUMO (eV) | Compute > Orbitals, sobre la estructura optimizada |

Después: pasar todo a Excel, ajustar `pIC50 = a·descriptor + b` para **cada** descriptor,
elegir el mejor, y combinar los dos mejores en `pIC50 = a·d₁ + b·d₂ + c`. Reportar el
análisis estadístico y el de ortogonalidad.

## TP 2 — docking

**Receptor:** transcriptasa reversa de HIV, archivo `2B6Adock.pdbqt`.

**Caja, literal del `conf.txt`:**

```
center_x = 5.642     size_x = 31     exhaustiveness = 10
center_y = -35.557   size_y = 31     spacing = 1.000
center_z = 22.358    size_z = 31     energy_range = 3
```
más los seis pesos de la función de scoring, que son los valores por defecto de Vina.

**Preparación de ligandos.** El camino estándar es HyperChem → .pdb → ADT → .pdbqt. El
anexo, para cuando ADT falla, indica el camino alternativo:

```
obabel *.hin -O *.mol2 --partialcharge gasteiger
obabel *.mol2 -O *.pdbqt
```

Esto importa: **el camino alternativo de la cátedra ya es OpenBabel con cargas Gasteiger,
que es exactamente lo que hace QuEtool.** No es una desviación nuestra, es el procedimiento
que la propia guía autoriza.

**Análisis.** Con ADT: `Analyze > Dockings > Show interactions`, con "Close contact",
"Hydrogen bonds" y etiquetas de residuo. Con ChimeraX (anexo): H-bonds con *Relax distance
and angle criteria*, tolerancia **1,0 Å** y **45°**, sólo *Intermodel*; y después
*contacts* con las mismas restricciones.

**Entregables (Sección V), cada uno vale 2 de 20 puntos:**

1. Un `.xlsx` con ΔG_dock de cada ligando junto a su pIC50.
2. Los parámetros estadísticos de la regresión `pIC50 = f(ΔG_dock)` y, si es
   significativa, su ecuación. Incluyendo el ΔG_dock del compuesto diseñado.
3. Descripción de las interacciones de cada ligando, destacando la comparación entre la
   red de contactos del compuesto diseñado y la de su precursor inmediato.
4. Si el modelo es significativo, predecir el pIC50 del nuevo compuesto y comparar con lo
   que predijo el modelo QSAR del TP 1: ¿coinciden?
5. Capturas de pantalla del ligando diseñado y de su precursor, mostrando las interacciones.

**Discusión (Sección VI):**

1. ¿Hay relación estadísticamente significativa entre ΔG_dock y pIC50?
2. ¿Se mantiene el patrón de interacciones a lo largo de la serie?
3. ¿El derivado propuesto conserva interacciones que aparecen en los otros ligandos?
4. Calcular **vLLE = −ΔG_dock/1,37 − logP** para el ligando diseñado y su precursor:
   ¿se espera una unión más eficiente?
5. Verdadero o falso, justificando: *"El modelo obtenido se encuentra validado y, por lo
   tanto, se podrán predecir compuestos potencialmente más activos"*.

## Qué cubre QuEtool hoy y qué no

QuEtool calcula: masa, clogP, refractividad, TPSA, superficie, dipolo, HOMO, LUMO y gap.

| Pide la guía | QuEtool | Nota |
|---|---|---|
| PM | ✔ masa | |
| logP | ✔ clogP | Wildman–Crippen en vez del método de HyperChem; los valores no van a coincidir |
| RM | ✔ refractividad | ídem |
| SA / SA-grid | ~ superficie | QuEtool da la ASA de Labute, que es una aproximación topológica, no la superficie sobre grilla con sonda de 1,4 Å |
| Momento dipolar | ✔ dipolo | GFN2 en vez de AM1 |
| HOMO, LUMO | ✔ | GFN2 en vez de AM1 |
| **Volume** | ✘ | **falta** |
| **Polarizability** | ✘ | **falta** |
| **Hydration Energy** | ✘ | **falta** |
| — | TPSA, gap | los da de más; el TP no los pide |

Los tres que faltan son calculables: volumen y polarizabilidad salen de la misma geometría
3D que ya se calcula, y la energía de hidratación necesita un modelo de solvatación
implícito —GFN2 trae ALPB, que habría que comprobar si está expuesto en occjs—.

## Qué falta para poder correr la réplica

No está en la carpeta conectada ni aparece en el Drive:

- **`2B6Adock.pdbqt`** — el receptor, de `materiales/Receptor/`.
- **Los 10 archivos `.hin`** de los NNRTI modelados en TP 1, de `materiales/Ligandos/`.
  Alternativamente, los SMILES de los diez.
- El **compuesto de diseño** y su precursor, si se quiere replicar también esa parte.

Todo eso está en el `materiales.zip` que la guía descarga desde Drive.
