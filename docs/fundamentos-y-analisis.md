# Herramienta web libre para los TP de QSAR y docking: fundamentos y análisis

**Proyecto:** reemplazo de la cadena de software propietario de los TP de Química Medicinal (FFyB-UBA) por un pipeline libre que corre íntegramente en el navegador.
**Destino editorial previsto:** *Journal of Chemical Education*, tipo Technology Report.
**Estado:** factibilidad técnica verificada experimentalmente (6 de noviembre de 2026). Sin bloqueos técnicos pendientes.

Este documento establece el problema, el encuadre bibliográfico y editorial, y el análisis de factibilidad con las mediciones que lo respaldan. No es una especificación ni un plan de trabajo.

---

## 1. El problema

### 1.1 Inventario de la cadena actual

Los TP 1 y 2 forman un flujo integrado que la propia guía diagrama como una sola cadena. El software involucrado es:

| Etapa | Programa | Estado |
|---|---|---|
| Modelado 3D y optimización de geometría | HyperChem | Comercial, Windows, discontinuado de hecho |
| Descriptores QSAR (Volume, logP, RM, polarizabilidad, masa, SAS-Grid) | HyperChem | ídem |
| Momento dipolar (AM1) y energías HOMO/LUMO | HyperChem | ídem |
| Preparación de ligandos (.pdb → .pdbqt) | MGLTools 1.5.6 / AutoDockTools | Sin mantenimiento activo |
| Docking | AutoDock Vina 1.2.7 + `batvina.bat` | Libre, pero por línea de comandos |
| Análisis de poses e interacciones | AutoDockTools | Sin mantenimiento activo |
| Regresión y estadística | MS Excel | Comercial |
| Ruta alternativa de contingencia | OpenBabel 3.1.1 + UCSF ChimeraX 1.12 | Libres |

### 1.2 Evidencia documentada de fragilidad

La cátedra tuvo que redactar un **documento anexo completo** con un procedimiento alternativo porque AutoDockTools no funciona correctamente en algunas computadoras con Windows 11 y drivers gráficos AMD. Esa es evidencia de primera mano, no una conjetura: el propio material de cátedra reconoce que la herramienta estándar falla y provee un camino de contingencia basado en OpenBabel y ChimeraX.

Este es el argumento de necesidad más fuerte del paper y conviene que encabece la introducción.

### 1.3 Puntos de fricción adicionales

- **Dependencia de Windows.** Instaladores `.exe`, CMD, rutas al "Escritorio de Windows", `batvina.bat`. Un estudiante con macOS, Linux o una máquina administrada no puede completar el TP.
- **Distribución por enlaces de Google Drive.** Sin versionado ni garantía de permanencia.
- **Cadena de formatos con cuatro programas.** `.hin` → `.pdb` → `.pdbqt` → `.log`/`.pdbqt`, cada salto un punto de falla.
- **Transcripción manual.** El valor de ΔG<sub>dock</sub> se lee abriendo el `.pdbqt` con Notepad y buscando la línea `REMARK VINA RESULT`; los residuos de contacto se tipean a mano en una tabla de doble entrada. Es tiempo que no se dedica a química y una fuente de error no trazable.
- **Instalación con permisos de administrador** para MGLTools, que muchas máquinas institucionales no otorgan.

### 1.4 Lo que no hay que tocar

El diseño pedagógico del TP es sólido y debe preservarse íntegro. Los objetivos declarados incluyen: condición de ortogonalidad entre descriptores; ajuste de modelos de una, dos y tres variables; pruebas de Fisher y de Student con α = 0,05; principio de parsimonia y sus condiciones de aplicabilidad; validez exclusiva de las comparaciones intra-modelo; interpretación fisicoquímica del modelo seleccionado; identificación de descriptores dependientes de la conformación; conservación del patrón de interacciones a lo largo de una serie; eficiencia de unión vía vLLE; y el ítem de verdadero/falso que confronta al estudiante con la afirmación "el modelo obtenido se encuentra validado y, por lo tanto, se podrán predecir compuestos potencialmente más activos".

Ese último ítem enseña explícitamente a resistir la sobreinterpretación de un modelo QSAR. Es lo más valioso del TP y la herramienta tiene que servirlo, no diluirlo.

---

## 2. Estado del arte y ubicación del aporte

### 2.1 Lo que ya está publicado

La entrada de estructuras en el navegador tiene historia y revisión propia (Ertl, *J. Cheminform.* 2010, 2:1). En educación química hay antecedentes concretos:

- **JSME** integrado para ejercicios de nomenclatura orgánica (Manh, Duong y Du, *World Journal of Chemical Education* 2017, 5(5), 164-167).
- **3DChemMol**, editor molecular 3D web evaluado con 54 estudiantes universitarios (*Acta Chim. Slov.* 2022).
- **Jmol Virtual Molecular Model Kit**, en uso desde 2010.
- **CH5M3D** (*J. Cheminform.* 2013, 5:46) y **Chemozart** (*J. Cheminform.* 2015, 7:56), editores y visualizadores 3D web.
- **Webina** (Kochnev, Hellemann, Cassidy y Durrant, *Bioinformatics* 2020, 36), que compila AutoDock Vina a WebAssembly y corre el docking entero en el navegador. Sus autores justifican el trabajo señalando que pedirle a un estudiante que descargue, instale y ejecute un programa de línea de comandos "a menudo resulta impracticable", y lo proponen explícitamente como herramienta para enseñar diseño de fármacos asistido por computadora.
- **atomistica.online** (*Molecular Simulation* 2024, 50(7-9)), interfaces web para xtb.

### 2.2 Dónde está el hueco

Un editor web libre para enseñar **no es novedad** y un paper que se presente así tiene poco recorrido con un referee.

El hueco real está aguas arriba del docking. Webina resuelve el docking en el navegador, pero **no existe el eslabón previo**: generar la estructura 3D, optimizarla y calcular el set de descriptores fisicoquímicos y electrónicos que el QSAR necesita, sin software propietario y sin instalar nada. Hoy ese eslabón es HyperChem.

El aporte, entonces, es el **pipeline completo QSAR + docking en el navegador**, con una pregunta pedagógica de química medicinal como hilo y la cadena de la cátedra como caso de uso real. El argumento de accesibilidad (sin licencias, sin instalación, sin sistema operativo obligatorio, sin permisos de administrador) tiene peso adicional en el contexto de una universidad pública argentina.

### 2.3 Encuadre editorial

**Journal of Chemical Education** es el destino adecuado. Es el journal oficial de la División de Educación Química de la ACS y cubre contenido, actividades, experimentos, métodos de enseñanza y pedagogía. El tipo de manuscrito que corresponde es **Technology Report**.

Existe un precedente de formato de dos papers que conviene considerar: el sitio *Orbital Explorer* se publicó como Technology Report y las actividades de aula que lo usan salieron en un artículo separado. Eso permitiría separar la herramienta de su evaluación pedagógica.

JCE exige designar el tipo de manuscrito al enviar, demostrar relevancia explícita para la enseñanza y el aprendizaje de la química, y definir claramente la audiencia. La extensión recomendada para un Technology Report es de **3000 palabras**, sin contar elementos gráficos, referencias ni material suplementario.

**Preprints.** JCE los admite de forma explícita: se puede depositar un borrador inicial en ChemRxiv, arXiv o bioRxiv. Hay tres condiciones: declarar el preprint en la carta de presentación, explicar los cambios introducidos entre el depósito y el envío, y enlazar el preprint al artículo por DOI una vez publicado. Publicar primero como preprint no cierra la puerta a JCE.

Entre los dos servidores, **ChemRxiv** es el natural para este trabajo: lo gobiernan en conjunto la ACS, la RSC, la GDCh y las sociedades química china y japonesa, cubre química medicinal y computacional, y varias revistas de la ACS permiten transferir directamente desde ahí a su sistema de manuscritos. arXiv también está admitido, pero su química vive en categorías de física y su categoría educativa es de física, no de química; además pide aval de un usuario establecido para quien publica por primera vez en una categoría.

**Dos revistas a no confundir:**
- *Education in Chemistry* (RSC) es una revista de divulgación bimestral, sin referato. No sirve.
- *Chemistry Education Research and Practice* (RSC) es de acceso abierto sin cargos para autores, pero está enfocada en investigación educativa con estudios sobre estudiantes. Para presentar una herramienta, JCE es el lugar natural.

---

## 3. Análisis de factibilidad técnica

Todo lo que sigue fue verificado experimentalmente, no inferido de documentación.

### 3.1 Componentes y licencias

| Componente | Versión | Licencia | Rol |
|---|---|---|---|
| OpenChemLib | 9.25.2 | BSD-3-Clause | Editor de dibujo, generación de conformeros 3D, MMFF94 |
| RDKit MinimalLib | 2026.09.2 | BSD-3-Clause | Descriptores 2D (logP, RM, masa, TPSA, ASA) |
| occjs (OCC) | 0.9.7 | — verificar | GFN2-xTB: optimización, HOMO/LUMO, multipolos CAMM |
| Ketcher | 3.18.0 | Apache-2.0 | Alternativa de editor, más completa |
| JSME | 2024.4.29 | BSD-3-Clause | Alternativa de editor, antecedente docente |
| Webina / AutoDock Vina | — | Apache-2.0 | Docking en el navegador |

La licencia de occjs quedó sin confirmar y es el único punto legal abierto; hay que verificarla antes de comprometerla en el manuscrito.

### 3.2 Mapeo de descriptores

| Descriptor del TP | Origen en HyperChem | Reemplazo libre | Estado |
|---|---|---|---|
| Optimización de geometría | Optimización + AM1 | OpenChemLib MMFF94 → GFN2 `--opt` | Verificado |
| logP | QSAR properties | RDKit `CrippenClogP` | Verificado, r² = 0,917 vs MOE |
| Refractividad molar (RM) | QSAR properties | RDKit `CrippenMR` | Verificado |
| Masa molecular | QSAR properties (mass) | RDKit `amw` | Verificado |
| Volumen | QSAR properties | RDKit 3D (`ComputeMolVolume`) | Verificado |
| Área superficial (SAS-Grid) | SAS-Grid, sonda 1,4 Å | RDKit `rdFreeSASA` / `labuteASA` | Equivalente conceptual, valores distintos |
| Polarizabilidad | QSAR properties | Derivable de RM (Lorenz-Lorentz) | No disponible directo |
| Momento dipolar | AM1 single point | Multipolos CAMM de GFN2, reconstruidos | Verificado |
| HOMO / LUMO | Compute > Orbitals | GFN2, salida directa | Verificado |

**Dos observaciones.** La polarizabilidad no está entre los 43 descriptores de MinimalLib, pero es casi colineal con la refractividad molar por la relación de Lorenz-Lorentz. Eso no es una pérdida: es el ejemplo didáctico ideal para el análisis de ortogonalidad que ya pide el TP. Y el momento dipolar no lo imprime `occ`: se reconstruye sumando cargas atómicas y dipolos atómicos CAMM del archivo de función de onda, lo que la herramienta deberá implementar.

### 3.3 Rendimiento medido

GFN2-xTB vía `occ tb`, sobre moléculas del rango de interés:

| Molécula | Átomos | Punto simple | Optimización |
|---|---|---|---|
| Efavirenz | 30 | 0,36 s | 13 pasos, 3,6 s |
| Nevirapina | 34 | — | 13 pasos, 4,4 s |
| Tiazolidinona 1 | 31 | — | 15 pasos, 5,1 s |

El rendimiento es mejor que el de HyperChem en la práctica de aula.

### 3.4 Restricción de carga

| Módulo | Tamaño |
|---|---|
| `occjs.wasm` | 25 MB |
| `occjs.data` | 8,4 MB |
| `RDKit_minimal.wasm` | 7,1 MB |

Alrededor de 40 MB en la primera carga. Se mitiga con carga diferida por etapa y caché, pero en una conexión pobre se va a notar y es una limitación honesta que el manuscrito debe declarar.

### 3.5 Lo que MinimalLib no tiene

La versión de RDKit que corre en el navegador (MinimalLib) **no expone generación de conformeros 3D ni minimización con campo de fuerzas**. Lo que parece serlo (`set_new_coords`) genera coordenadas 2D de dibujo. Este era el bloqueo principal del proyecto y quedó resuelto por OpenChemLib, que trae `ConformerGenerator` y `ForceFieldMMFF94` en JavaScript puro, sin WASM.

Detalle de implementación: ambas clases fallan con el error `static resources must be registered first` si no se invoca previamente `Resources.register()` con el `resources.json` de la librería.

---

## 4. Validación: replicación del caso de la Parte A

Para verificar que el stack libre cubre los contenidos sin depender de estudiantes, se replicó el caso de literatura que el TP usa en su Parte A: Rawal, Prabhakar, Katti y De Clercq, *Bioorg. Med. Chem.* 2005, 13(24), 6771-6776, serie de 15 tiazolidin-4-onas con actividad anti-HIV, descriptores originales calculados con MOE.

### 4.1 Procedimiento

Se construyeron los 15 SMILES desde la tabla de sustituyentes de la guía y se **verificó por código** la posición de cada sustituyente respecto del carbono ipso, no solo la fórmula molecular: 15 de 15 correctos. Las geometrías se generaron con OpenChemLib (conformero + MMFF94) y se optimizaron con GFN2.

### 4.2 Transferencia de los descriptores

| Comparación | r | r² | p |
|---|---|---|---|
| clogP (Crippen) vs logP (MOE) | +0,958 | 0,917 | < 0,0001 |
| dipolo (GFN2) vs µ(MNDO) | +0,144 | 0,021 | 0,61 |
| ídem, excluyendo el compuesto 11 | +0,575 | 0,331 | 0,031 |

La lipofilicidad transfiere casi perfectamente entre implementaciones. El dipolo, no, y la razón es instructiva.

### 4.3 Un probable error en la tabla publicada

El compuesto 11 es el 2′,4′,6′-trimetoxifenilo. La tabla le asigna µ(MNDO) = 0,012 D y E<sub>oop</sub> = 4,189, mientras que el resto de la serie tiene E<sub>oop</sub> entre 0,005 y 0,100. Un momento dipolar de 0,012 D es químicamente implausible para ese compuesto, y GFN2 le asigna 5,68 D, el mayor de toda la serie.

Si se asume que ambos valores están transpuestos y se usa µ = 4,189, la correlación con el dipolo GFN2 pasa de r = 0,144 a **r = 0,649 (p = 0,0088)**.

No es demostrable sin consultar el original, pero la evidencia numérica es consistente con una transposición que la guía de TP viene arrastrando. Como ítem de clase es excelente: detectar el dato anómalo y argumentar por qué no puede ser correcto.

### 4.4 Los modelos QSAR

Con descriptores libres (α = 0,05):

| Modelo | R² | R²adj | F | p(F) | Significancia de coeficientes |
|---|---|---|---|---|---|
| clogP | 0,317 | 0,265 | 6,04 | 0,029 | clogP p = 0,029 |
| dipolo | 0,183 | 0,120 | 2,91 | 0,112 | no significativo |
| HOMO | 0,008 | −0,068 | 0,11 | 0,749 | no significativo |
| gap | 0,190 | 0,128 | 3,05 | 0,104 | no significativo |
| MR | 0,062 | −0,010 | 0,86 | 0,372 | no significativo |
| **clogP + dipolo** | **0,650** | **0,591** | **11,13** | **0,0018** | clogP p = 0,002 · dipolo p = 0,006 |
| clogP + HOMO | 0,401 | 0,301 | 4,02 | 0,046 | HOMO p = 0,220 |
| clogP + dipolo + gap | 0,667 | 0,576 | 7,34 | 0,006 | gap p = 0,470 |

Y el mismo modelo de dos variables con los descriptores **publicados**:

| Modelo | R² | R²adj | F | p(F) | Significancia |
|---|---|---|---|---|---|
| logP(MOE) + µ(MNDO) | 0,528 | 0,450 | 6,72 | 0,011 | logP p = 0,007 · **µ p = 0,116** |

El resultado central: **el stack libre produce un modelo mejor que el de los descriptores publicados y llega a la misma conclusión química** que declara el abstract del paper original, el rol de la lipofilicidad y del momento dipolar, con ambos coeficientes positivos y significativos. Con los descriptores publicados, el dipolo no alcanza significancia.

El modelo de tres variables ilustra la parsimonia con precisión de manual: R² sube a 0,667 pero R²adj baja a 0,576 y el tercer descriptor sale con p = 0,470.

### 4.5 Ortogonalidad

Matriz de |r| entre descriptores libres, valores salientes:

| Par | \|r\| | Lectura |
|---|---|---|
| MR – Volumen | 0,92 | Colineales: la misma información |
| LUMO – gap | 0,95 | Colineales por construcción |
| HOMO – LUMO | 0,90 | Fuertemente acoplados |
| Volumen – TPSA | 0,90 | Colineales |
| **clogP – dipolo** | **0,24** | Par ortogonal, el que sostiene el modelo |

El ejercicio de ortogonalidad del punto 1 de la guía se reproduce con ejemplos más nítidos que los originales.

### 4.6 Dependencia conformacional, medida

Se corrió la cadena dos veces con sembrado 3D distinto (OpenChemLib en JavaScript frente a RDKit en Python) y se compararon los descriptores resultantes:

| Descriptor | r entre cadenas | Diferencia media absoluta |
|---|---|---|
| HOMO | +0,988 | 0,034 eV |
| Momento dipolar | +0,759 | 0,57 D |

Los dos peores casos del dipolo son los compuestos 7 y 10, con diferencias de +1,91 D y +2,13 D, y son precisamente los que tienen metoxilos rotables.

Esto responde empíricamente la **pregunta 1 de discusión de la Parte B**, que pide indicar qué descriptores dependen de la conformación molecular, cómo evidenciarlo y explicarlo en términos fisicoquímicos. Con este stack el estudiante lo mide en lugar de que se lo afirmen: genera dos confórmeros y observa cuál descriptor se mueve y cuál permanece.

### 4.7 El modelo con la cadena íntegramente de navegador

Repitiendo el modelo seleccionado sin ningún componente de Python:

**pEC50 = f(clogP, dipolo):** R² = 0,596 · R²adj = 0,529 · F = 8,86 · p(F) = 0,0043 · clogP = +1,664 (p = 0,0015) · dipolo = +0,463 (p = 0,0138)

Ambos descriptores significativos, ambos positivos, misma conclusión química, y todavía mejor que el modelo construido con los descriptores publicados.

---

## 5. Cobertura de los contenidos del TP

| Contenido de la guía | Cobertura |
|---|---|
| Modelado 3D y optimización de geometría | Cubierto (OpenChemLib + GFN2) |
| Set completo de descriptores fisicoquímicos | Cubierto, salvo polarizabilidad directa |
| Momento dipolar y HOMO/LUMO | Cubierto |
| Condición de ortogonalidad entre descriptores | Cubierto, con mejores ejemplos |
| Modelos de 1, 2 y 3 variables | Cubierto |
| Pruebas de Fisher y Student, α = 0,05 | Cubierto |
| Principio de parsimonia | Cubierto, caso limpio |
| Interpretación fisicoquímica del modelo | Cubierto, misma conclusión que el paper |
| Descriptores dependientes de conformación | Cubierto y ahora medible, no solo enunciable |
| Docking y ΔG<sub>dock</sub> | Vía Webina, pendiente de integración |
| Red de interacciones ligando-receptor | Pendiente de diseño |
| Regresión pIC50 = f(ΔG<sub>dock</sub>) | Cubierto |
| vLLE | Cubierto (fórmula sobre ΔG<sub>dock</sub> y logP) |
| Ítem crítico verdadero/falso sobre validación | Preservado, no depende de la herramienta |

---

## 6. Riesgos y decisiones abiertas

### 6.1 Riesgos técnicos

- **Verificación en navegador real.** Todo lo medido corrió bajo Node usando los mismos módulos WASM y JavaScript, pero no dentro de un navegador. Webina usa `SharedArrayBuffer`, que varios navegadores deshabilitaron y que requiere cabeceras específicas del servidor. Es el próximo punto a confirmar.
- **Licencia de occjs** sin verificar.
- **Peso de la primera carga**, alrededor de 40 MB.

### 6.2 Decisiones de diseño pendientes

- **Manejo de confórmeros.** El resultado de 4.6 obliga a decidir: un solo confórmero, el de menor energía, o un ensemble con promedio de Boltzmann. Con el primer confórmero disponible, dos estudiantes con la misma molécula pueden reportar dipolos distintos. La decisión tiene peso pedagógico además de técnico, y puede convertirse en contenido explícito.
- **GFN2 no es AM1.** Los valores no reproducirán los de HyperChem ni los de MOE. No es un obstáculo: la guía ya advierte que solo las comparaciones intra-modelo son válidas, el paper original usó MOE y el TP usa HyperChem, de modo que la discrepancia entre métodos ya está presente en el material actual. Puede explicitarse como contenido sobre dependencia del descriptor respecto del método de cálculo.
- **Integración frente a encadenamiento.** Alimentar a Webina con la salida de la herramienta es mucho menos trabajo y da un paper igualmente publicable. Integrar todo en una sola aplicación es más ambicioso y se parece más a una tesis de computación. Webina consume receptor y ligando en formato PDBQT, lo que define la salida requerida si se opta por encadenar.
- **Alcance del artículo.** Un Technology Report único, o el modelo de dos papers con la herramienta y las actividades por separado.

### 6.3 Condiciones que impone el piloto con estudiantes

El piloto está previsto para el ciclo 2027 y su calendario corre hacia atrás desde la clase en que se use la herramienta, no desde el inicio del cuatrimestre.

- **Aval ético y consentimiento informado.** Requisito confirmado en las guías de autor de JCE. Hay que identificar el comité de ética o IRB que aprobó el trabajo y su número de aprobación; si no hizo falta revisión formal, hay que explicar por qué. Se exige además una declaración de consentimiento informado cuando el estudio involucra interacción directa con participantes identificables, trabajos de estudiantes o datos personales, y para datos anónimos o agregados hay que explicar cómo se preservó la confidencialidad. Todo eso va en la sección de métodos. La documentación del consentimiento de los estudiantes se sube como material aparte, y los nombres completos no pueden aparecer ni en el manuscrito ni en el material suplementario. Las guías advierten que una presentación sin documentación suficiente puede ser rechazada. En la UBA implica el comité o la instancia que corresponda en FFyB. Es el trámite más lento y por eso condiciona todo lo demás.
- **Instrumentos diseñados antes del curso.** Pre-test y post-test sobre los contenidos específicos, encuesta de usabilidad estandarizada, y eventualmente comparación entre comisiones. Varios ítems de las secciones de discusión del TP sirven casi tal cual, en particular el de verdadero/falso y la pregunta de dependencia conformacional.
- **Estabilidad de la herramienta semanas antes de la clase en que se use**, no al comienzo del cuatrimestre.
- **La validación técnica no depende del piloto.** La sección 4 de este documento ya constituye resultados publicables. Si el piloto se complica, el paper no queda sin evidencia.

---

## 7. Referencias

1. Rawal, R. K.; Prabhakar, Y. S.; Katti, S. B.; De Clercq, E. 2-(Aryl)-3-furan-2-ylmethyl-thiazolidin-4-ones as selective HIV-RT inhibitors. *Bioorg. Med. Chem.* **2005**, *13*(24), 6771-6776. DOI: 10.1016/j.bmc.2005.07.063
2. Kochnev, Y.; Hellemann, E.; Cassidy, K. C.; Durrant, J. D. Webina: an open-source library and web app that runs AutoDock Vina entirely in the web browser. *Bioinformatics* **2020**, *36*. DOI: 10.1093/bioinformatics/btaa579
3. Ertl, P. Molecular structure input on the web. *J. Cheminform.* **2010**, *2*:1. DOI: 10.1186/1758-2946-2-1
4. Manh, H. D.; Duong, N. T. T.; Du, C. V. JSME Molecular Editor: a tool for creating interactive web-based organic chemistry exercises. *World Journal of Chemical Education* **2017**, *5*(5), 164-167. DOI: 10.12691/wjce-5-5-4
5. Mohebifar, M.; Sajadi, F. Chemozart: a web-based 3D molecular structure editor and visualizer platform. *J. Cheminform.* **2015**, *7*:56. DOI: 10.1186/s13321-015-0101-7
6. CH5M3D: an HTML5 program for creating 3D molecular structures. *J. Cheminform.* **2013**, *5*:46. DOI: 10.1186/1758-2946-5-46
7. The students' perceptions using 3DChemMol molecular editor for construction and editing of molecular models. *Acta Chim. Slov.* **2022**.
8. Online and desktop graphical user interfaces for xtb programme from atomistica.online platform. *Molecular Simulation* **2024**, *50*(7-9). DOI: 10.1080/08927022.2024.2329736
9. Rothenberger, O.; Newton, T. A.; Hanson, R. M.; Sitzmann, M. The Jmol Virtual Molecular Model Kit: a resource for teaching and learning chemistry. ConfChem, **2011**.

**Material de cátedra utilizado como fuente primaria:** guía del TP 2 (QSAR, Partes A y B), guía del TP 2 de docking molecular, documento anexo con el procedimiento alternativo, y el paper de referencia de la Parte A.
