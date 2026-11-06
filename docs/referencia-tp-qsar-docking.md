# Referencia: TP de QSAR y docking molecular (Química Medicinal, FFyB-UBA)

Destilado de las guías de cátedra vigentes, pensado como insumo para generar especificaciones de la herramienta web que reemplaza la cadena de software propietario. Recoge **lo que los TP exigen**, no lo que la herramienta debería ser.

Fuentes: guía del TP 2 de QSAR (Partes A y B), guía del TP 2 de docking molecular, documento anexo con el procedimiento alternativo, y Rawal, Prabhakar, Katti y De Clercq, *Bioorg. Med. Chem.* 2005, 13(24), 6771-6776.

---

## 1. La cadena integrada

Los TP 1 y 2 son un único flujo. El esquema de la guía lo encadena así:

```
TP 1                                        TP 2
────                                        ────
Ligandos NNRTI (10, IC50 de literatura)
   └─> HyperChem: estructura 3D + descriptores
          └─> MS Excel: modelo QSAR
                 └─> diseño de análogo
                        └─> HyperChem: estructura 3D + descriptores
                               └─> MS Excel: IC50 calculada (QSAR)
                                      │
                                      ├─> MGLTools: preparación de estructuras
                                      ├─> GridBox + archivo de configuración
                                      ├─> AutoDock Vina: experimentos de docking
                                      ├─> MGLTools: análisis de poses y scores
                                      ├─> modelo pIC50 = f(ΔGdock)
                                      └─> comparación de modos de unión
```

Cualquier herramienta que reemplace un eslabón tiene que entregar la entrada del siguiente.

---

## 2. Parte A — Caso de literatura

### 2.1 Sistema

Farmacomodulación desde el precursor **TBZ1** hacia una serie de 15 **2-(aril)-3-furan-2-ilmetil-tiazolidin-4-onas (TZDs)**, evaluadas *in vitro* sobre replicación de HIV-1 IIIb en células MT-4.

Núcleo común: 2-aril-3-(furan-2-ilmetil)-tiazolidin-4-ona. Varía solo el patrón de sustitución del anillo arilo.

### 2.2 Serie y actividad

| TZD | R2′ | R3′ | R4′ | R5′ | R6′ | EC50 [µM] |
|---|---|---|---|---|---|---|
| 1 | Cl | H | H | H | Cl | 0,204 |
| 2 | F | H | H | H | F | 2,88 |
| 3 | Cl | H | H | H | F | 0,576 |
| 4 | H | H | Cl | H | H | 43,54 |
| 5 | Cl | H | H | H | H | 6,43 |
| 6 | H | Cl | H | Cl | H | 42,16 |
| 7 | OCH₃ | H | H | H | H | 57,78 |
| 8 | H | H | OCH₃ | H | H | 85,64 |
| 9 | OCH₃ | H | OCH₃ | OCH₃ | H | 262,69 |
| 10 | H | OCH₃ | OCH₃ | OCH₃ | H | 358,17 |
| 11 | OCH₃ | H | OCH₃ | H | OCH₃ | 6,88 |
| 12 | CH₃ | H | H | H | H | 29,08 |
| 13 | CH₃ | H | H | H | CH₃ | 7,80 |
| 14 | F | F | F | F | F | 46,85 |
| 15 | 1-naftilo | | | | | 5,53 |

### 2.3 Descriptores publicados (calculados con MOE)

- **logP** — logaritmo de la constante de partición octanol/agua.
- **µ(MNDO)** — momento dipolar por el método semiempírico MNDO.
- **Eoop** — energía torsional *out-of-plane* de la rotación de los grupos aromáticos; indicador de flexibilidad molecular.

| TZD | EC50 [µM] | logP | µ(MNDO) | Eoop |
|---|---|---|---|---|
| 1 | 0,204 | 3,485 | 3,169 | 0,094 |
| 2 | 2,88 | 2,607 | 3,758 | 0,006 |
| 3 | 0,576 | 3,327 | 4,463 | 0,030 |
| 4 | 43,54 | 2,897 | 1,779 | 0,034 |
| 5 | 6,43 | 2,895 | 3,376 | 0,065 |
| 6 | 42,16 | 3,600 | 0,778 | 0,009 |
| 7 | 57,78 | 2,259 | 3,147 | 0,008 |
| 8 | 85,64 | 2,261 | 3,221 | 0,006 |
| 9 | 262,69 | 1,995 | 2,424 | 0,028 |
| 10 | 358,17 | 1,746 | 2,841 | 0,051 |
| 11 | 6,88 | 2,243 | **0,012** | **4,189** |
| 12 | 29,08 | 2,601 | 2,210 | 0,081 |
| 13 | 7,80 | 2,897 | 2,209 | 0,100 |
| 14 | 46,85 | 3,058 | 1,038 | 0,005 |
| 15 | 5,53 | 3,525 | 2,467 | 0,027 |

> **Anomalía detectada.** Para el compuesto 11 (2′,4′,6′-trimetoxifenilo) la tabla asigna µ = 0,012 D y Eoop = 4,189, mientras el resto de la serie tiene Eoop entre 0,005 y 0,100. Un cálculo GFN2 le asigna 5,68 D, el mayor de la serie. La evidencia numérica es consistente con una transposición de ambos valores: asumiendo µ = 4,189, la correlación con el dipolo calculado pasa de r = 0,144 a r = 0,649 (p = 0,0088). Sirve como ítem de detección de outliers.

### 2.4 Modelos que plantea la guía

- pEC50 = f(logP, µMNDO)
- pEC50 = f(logP, µMNDO, Eoop)

### 2.5 Consignas de análisis

1. Demostrar si se cumple la **condición de ortogonalidad** para todas las combinaciones posibles de descriptores.
2. Ajustar todos los modelos de **regresión lineal** posibles: de una, dos y hasta tres variables independientes.
3. **Análisis estadístico** de cada modelo y selección del mejor, incluyendo pruebas de **Fisher** y de **Student** con **α = 0,05**.
4. Interpretar el modelo seleccionado en **términos biológicos**: de qué propiedades estructurales depende la maximización de la actividad.
5. Indicar **al menos dos formas** de validar el poder predictivo del modelo.
6. Indicar qué condiciones deben cumplirse para aplicar el **principio de parsimonia**.

---

## 3. Parte B — Cálculo de descriptores y modelos propios

Se parte de las estructuras del set de INNTRs modeladas en el TP anterior.

### 3.1 Descriptores a calcular y su procedencia exacta en HyperChem

| Descriptor | Ruta en HyperChem | Parámetros |
|---|---|---|
| Volumen (*Volume*) | Compute > QSAR properties | Options > Calculation options: tipo *Solvent accessible surface*, Solvent Probe Radius **1,4 Å**, Points On Cube Side **50** |
| log P | Compute > QSAR properties | — |
| Refractividad (RM) | Compute > QSAR properties | — |
| Polarizabilidad | Compute > QSAR properties | — |
| Peso molecular (*mass*) | Compute > QSAR properties | — |
| Área superficial (SAS-Grid) | Compute > QSAR properties | mismos parámetros que Volume |
| Momento dipolar | Compute > Single Point (**AM1**) → Compute > Properties… | sobre la estructura ya optimizada |
| Energías HOMO y LUMO | Compute > Orbitals… | leer el campo *Energy* de cada orbital |

### 3.2 Flujo de modelado

1. Transcribir los descriptores a una planilla de Excel.
2. Obtener un modelo lineal **por cada descriptor**, de la forma `pIC50 = a · descriptor + b`, con Datos > Análisis de Datos > Regresión.
3. Seleccionar el mejor modelo de la serie según su perfil estadístico y reportarlo.
4. Tomar los **dos mejores** y combinarlos en `pIC50 = a · descriptor1 + b · descriptor2 + c`.
5. Reportar ese modelo con su análisis estadístico, indicar si supera al anterior y justificar.
6. Incluir el **análisis de ortogonalidad** correspondiente.

### 3.3 Elementos de discusión

1. Qué descriptores de la serie tienen **valores dependientes de la conformación molecular**. Cómo evidenciarlo y explicarlo fisicoquímicamente.
2. Significado de **cada parámetro estadístico** en el marco de los criterios de decisión adoptados.
3. Según el modelo elegido, qué descriptores influyen en la actividad y **cómo debe modificarse** la propiedad para optimizarla.
4. **Fortalezas y límites** de esta clase de modelado estructura-actividad.

---

## 4. TP 2 — Docking molecular

### 4.1 Sistema

10 compuestos NNRTI con IC50 de literatura, más **un compuesto de diseño propio** cuya actividad se infirió por QSAR. Receptor: transcriptasa reversa de HIV, archivo `2B6Adock.pdbqt`.

### 4.2 Configuración del experimento (`conf.txt`, textual)

```
center_x = 5.642
center_y = -35.557
center_z = 22.358
size_x = 31
size_y = 31
size_z = 31
exhaustiveness = 10
spacing = 1.000
energy_range = 3
weight_gauss1 = -0.035579
weight_gauss2 = -0.005156
weight_repulsion = 0.840245
weight_hydrophobic = -0.035069
weight_hydrogen = -0.587439
weight_rot = 0.05846
```

### 4.3 Procedimiento actual, por etapas

**Instalación.** MGLTools 1.5.6 (instalador `.exe`, **requiere permisos de administrador**, ruta fija `C:\Program Files (x86)\MGLTools-1.5.6`) y `vina.exe` 1.2.7. Distribuidos en un `materiales.zip` vía enlace de Google Drive, a descomprimir en el Escritorio de Windows.

**Preparación de ligandos.** `.hin` → abrir en HyperChem → guardar como `.pdb` con casillas *Hydrogens* y *Connectivity* marcadas → abrir en ADT → Ligand > Output > Save as PDBQT → repetir uno por uno.

**Ejecución.** Desde CMD en la carpeta `materiales`, ejecutar `batvina.bat`, que recorre cada `.pdbqt` de la carpeta `Ligandos` contra el receptor y vuelca `.log` y `.pdbqt` en `Resultados`.

**Análisis.** En ADT: Analyze > Dockings > Open AutoDock vina result, cargando como *Single molecule with multiple conformations*; cargar el receptor; Analyze > Dockings > Show interactions con las opciones **Close contact**, **Hydrogen bonds** y **display labels on residues**.

**Registro.** Tabla de doble entrada: nombre del ligando | ΔGdock | un residuo contactado por columna. Se tipea a mano.

### 4.4 Entregables (Sección V)

1. Archivo `.xlsx` con ΔGdock de cada ligando y sus pIC50, **incluyendo el ligando de diseño propio**. La primera hoja debe ser el mejor modelo QSAR del TP 1.
2. Parámetros estadísticos de la regresión que justifiquen el modelo, y la ecuación si resulta significativo.
3. Descripción de las interacciones, destacando la comparación entre la red de contactos del compuesto diseñado y la de su precursor inmediato.
4. Si `pIC50 = f(ΔGdock)` es significativo, predicción de pIC50 del nuevo compuesto y comparación con la predicción del modelo QSAR.
5. Capturas de pantalla de las poses del ligando diseñado y de su precursor, mostrando las interacciones.

### 4.5 Discusión (Sección VI)

1. ¿Hay relación estadísticamente significativa entre ΔGdock y pIC50? Justificar con los parámetros del modelo.
2. ¿Se mantiene el **patrón de interacciones** a lo largo de la serie?
3. ¿El derivado propuesto conserva interacciones presentes en los otros complejos?
4. Eficiencia de unión por **vLLE**, comparando el ligando diseñado contra su precursor:

   `vLLE = -ΔGdock / 1,37 - logP`

5. Verdadero o falso, justificando si es falso:

   > *"El modelo obtenido se encuentra validado y, por lo tanto, se podrán predecir compuestos potencialmente más activos"*

### 4.6 Rúbrica

Cada ítem de las secciones V y VI, completo y correcto, aporta **2 puntos** sobre **20**.

---

## 5. El procedimiento alternativo del anexo

La cátedra documenta que **AutoDockTools puede no funcionar** (el anexo menciona explícitamente computadoras con drivers gráficos AMD sobre Windows 11) y provee una ruta de contingencia con OpenBabel 3.1.1 y UCSF ChimeraX 1.12, también distribuidos por enlaces de Google Drive.

**Preparación alternativa de ligandos**, desde CMD:

```
obabel *.hin -O *.mol2 --partialcharge gasteiger
obabel *.mol2 -O *.pdbqt
```

**Análisis alternativo en ChimeraX:** cargar receptor y pose; Tools > Structure Analysis > **H-bonds** con *Relax distance and angle criteria*, tolerancia de distancia **1,000** y de ángulo **45**, *Limit by selection* en *with at least one end selected*, solo *Intermodel*, *Reveal atoms* activo. Luego Tools > Structure Analysis > **contacts** con los mismos límites, *Ignore hidden models* y *Reveal atoms of interacting residues*.

**Lectura del ΔGdock:** abrir el `.pdbqt` de resultados con un editor de texto y leer la línea `REMARK VINA RESULT`.

Este anexo es la evidencia documental de fragilidad de la cadena actual.

---

## 6. Requisitos funcionales que se desprenden

Lo que una herramienta debe cubrir para servir estos TP sin degradar el contenido.

### 6.1 Construcción de estructuras
- Dibujo de estructuras 2D e ingreso por SMILES.
- Generación de coordenadas 3D y optimización de geometría.
- Manejo explícito de hidrógenos y de conectividad (lo que hoy exigen las casillas del diálogo de HyperChem).
- Exportación a PDBQT, formato que consumen Vina y Webina.

### 6.2 Descriptores
- El set completo de 3.1: volumen, logP, refractividad molar, polarizabilidad, masa, área superficial, momento dipolar, HOMO y LUMO.
- Superficie y volumen definidos como superficie accesible al solvente con sonda de 1,4 Å, para mantener la correspondencia conceptual.
- Exportación directa a tabla, sin transcripción manual.

### 6.3 Estadística
- Regresión lineal simple y múltiple, de una a tres variables.
- Prueba de Fisher y prueba de Student, con α configurable y 0,05 por defecto.
- R² y R² ajustado, para que el principio de parsimonia sea visible.
- Matriz de correlación entre descriptores para el análisis de ortogonalidad.

### 6.4 Docking
- Configuración de GridBox por coordenadas y tamaño, con los parámetros de 4.2.
- Ejecución por lotes sobre un conjunto de ligandos contra un receptor.
- Lectura automática de ΔGdock: nada de abrir archivos con un editor de texto.
- Detección de puentes de hidrógeno y contactos cercanos, con **identificación de residuos por nombre**.
- Generación automática de la tabla de doble entrada ligando × residuo.
- Visualización de la pose y captura de imagen exportable para el informe.

### 6.5 Cálculos derivados
- pIC50 y pEC50 a partir de concentraciones en µM.
- vLLE según la fórmula de 4.5.

### 6.6 Restricciones de contenido que la herramienta no debe romper
- Solo son válidas las **comparaciones intra-modelo**; la herramienta no debe sugerir comparaciones entre modelos distintos.
- La **dependencia conformacional** de ciertos descriptores debe seguir siendo observable por el estudiante, no quedar oculta tras un valor único.
- La herramienta **no debe insinuar** que un modelo validado habilita a predecir compuestos más activos: ese es justamente el ítem crítico de la rúbrica.

---

## 7. Parámetros numéricos, resumen

| Parámetro | Valor |
|---|---|
| Nivel de significancia | α = 0,05 |
| Sonda de solvente (SAS, volumen) | 1,4 Å |
| Points On Cube Side | 50 |
| Método semiempírico original | AM1 (descriptores propios), MNDO (paper) |
| GridBox, centro | (5,642 · −35,557 · 22,358) |
| GridBox, tamaño | 31 × 31 × 31 |
| Exhaustiveness | 10 |
| Spacing | 1,000 |
| Energy range | 3 |
| Tolerancia de distancia, H-bonds (ChimeraX) | 1,000 |
| Tolerancia de ángulo, H-bonds (ChimeraX) | 45 |
| Constante de vLLE | 1,37 |
| Puntaje por ítem de informe | 2 sobre 20 |
