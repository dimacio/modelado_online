# Banco de análisis de docking — planteo de diseño

> **Sobre los nombres.** El programa educativo, el que está publicado, se llama **QuEtool**
> (herramienta de química educativa). **BetaTools** queda reservado para el canal de pruebas:
> donde se estrena cada funcionalidad nueva antes de que pase a QuEtool. La herramienta de
> investigación que describe este documento **todavía no tiene nombre**; acá se la llama
> "el banco de análisis".
>
> Documento de diseño, no especificación. Fija el problema, el modelo de datos y los
> límites; las tareas concretas salen después. Escrito el 2026-11-09, antes de escribir
> una línea de código, sobre datos reales del repo `dimacio/quimioteca-gaussian`.

## 1. El problema

El artefacto de análisis que ya existe (`Clusters de docking`) hace mucho y lo hace bien:
visor 3D del complejo, PCA de poses con ejes en ångström, dendrograma de enlace completo
sobre RMSD, huella de contactos tipo SIFt, red de interacciones estilo LigNetwork, funnel
plot de ΔG contra distancia al sitio. El problema no es lo que muestra.

El problema es **de dónde lo saca**. Los datos están horneados en siete archivos publicados
junto a la página: `embed.json` con los PCA y UMAP precalculados, `poses.json` con las
coordenadas, y un PDBQT por receptor. Todo eso lo produjo un script de Python fuera de la
página. Para mirar una corrida nueva hay que volver a correr ese script, regenerar los JSON
y republicar. Y la estructura de los datos está grabada en el código: `DATA[receptor][carga][ligando]`
asume que las condiciones de este proyecto en particular —receptor, método de carga— son
las únicas que pueden existir, y `META.sitios` tiene las coordenadas del sitio de referencia
escritas a mano.

Es una foto excelente de una corrida. No es un instrumento.

**El banco de análisis es ese mismo análisis convertido en instrumento**: le das los archivos que
tengas, los lee en el navegador y analiza. La quimioteca de cisteín-proteasas es el caso
de prueba, no el contenido.

## 2. Qué es y qué no es

**Es** un banco de análisis de resultados de docking. Lee corridas ya hechas, las cruza con
descriptores calculados por otro lado y produce las figuras y las tablas con las que se
decide qué compuesto sigue.

**No es** un reemplazo de AutoDock ni de Gaussian. No corre DFT, no corre dinámica, no
re-dockea. Esa parte sigue donde está, en neocortex con GPU. El banco empieza donde
termina el cómputo pesado.

**No es QuEtool con más botones.** QuEtool enseña: una molécula por vez, todo explicado,
sin preparación previa. El banco asume que sabés lo que estás mirando y trabaja con cientos
de corridas a la vez. Son dos públicos y dos ritmos distintos.

## 3. Relación con QuEtool

Viven en el mismo repo, en `gama/`, y comparten el núcleo. Lo que se comparte es lo que ya
está escrito y probado en QuEtool:

- el lector de PDBQT (átomos, tipos AutoDock, residuos),
- el análisis geométrico de interacciones (puente de hidrógeno con ángulo D–H···A, contacto
  hidrofóbico, apilamiento π–π, enlace de halógeno, puente salino) con sus umbrales,
- el armado del complejo en 3Dmol y el dibujo de las interacciones,
- la paleta y los componentes de interfaz.

Eso pasa a un módulo `comun/` que importan los dos. La razón no es ahorrar líneas: es que
**el criterio con el que se mide un puente de hidrógeno tiene que ser el mismo** en la
herramienta con la que aprenden los estudiantes y en la que usás para decidir qué sintetizar.
Si divergen, el día que un estudiante compare su resultado con el tuyo vas a tener una
discusión que no es sobre química.

## 4. El modelo de datos

Es el centro del diseño y la diferencia real con el artefacto.

```
Proyecto
├── receptores  id → { texto, átomos, sitio de referencia }
├── ligandos    id → { nombre, atributos: { columna → valor } }
└── corridas    [ { receptor, ligando, condición, motor, clusters[] } ]

condición = { caja, carga, etiqueta }      ← libre, no un enum fijo
cluster   = { rank, n, ΔG_min, ΔG_medio, RMSD_ref?, poses[] }
pose      = { run, ΔG, átomos[] }
```

Cuatro decisiones que importan:

**La unidad es la corrida, no el ligando.** Una corrida es la tripla (receptor, ligando,
condición). En el artefacto el anidado `DATA[receptor][carga][ligando]` fija que las
condiciones son exactamente dos ejes. Los datos reales ya no entran en ese molde: en
`ranking.csv` hay 1548 corridas sobre **11 combinaciones de receptor y caja** —6W63, 6LU7,
7LBR, 7QCH, más variantes `_blind` y `_null`— por 2 métodos de carga por hasta 91 ligandos.
Y el próximo proyecto va a variar otra cosa: el pH, el estado de protonación, la versión del
campo de fuerzas. La condición tiene que ser un registro con etiqueta libre, no dos niveles
de objeto.

**El sitio de referencia se define, no se hornea.** En el artefacto las coordenadas están en
`META.sitios`. En el banco el sitio de un receptor se fija cargando un ligando de referencia
—el cristalográfico— y tomando su centroide, o escribiendo las coordenadas a mano. Esto no es
cosmética: tu propio `CLAUDE.md` registra que la caja enfocada de 7QCH está sobre A5I, **a
30 Å de la Cys111 catalítica**, o sea en un sitio de interacción proteína-proteína y no en el
catalítico. Una herramienta donde el sitio es un dato que se declara y cuya distancia se
muestra en cada tabla hace que esa clase de cosa salte a la vista en vez de quedar enterrada
en un comentario.

**Los atributos del ligando entran por CSV y se unen por id.** Cualquier columna numérica
—HOMO, LUMO, gap, μ, η, ω, dipolo, cargas CM5— queda disponible para graficar y correlacionar
sin que yo escriba su nombre en ningún lado. Es lo que permite preguntar "¿el gap predice el
ΔG?" sin tocar código.

**La unión parcial se muestra, no se descarta.** `ranking.csv` tiene 91 ligandos y
`docking_vs_dft.csv` tiene 74. Los 17 que faltan son exactamente los `tdz*_e2`: el otro
isómero de las tiadiazolinas, dockeado pero sin DFT en esa tabla. Si la herramienta hiciera
el *join* en silencio, estarías comparando isómeros sin enterarte. Entonces: toda unión
reporta cuántos quedaron afuera y quiénes son, y eso viaja en el CSV exportado.

## 5. Qué sabe leer

Verificado contra los archivos reales del repo, no contra la documentación de los formatos:

| Formato | Qué se saca | Estado |
|---|---|---|
| `.dlg` de AutoDock-GPU / AutoDock4 | clusters (rango, ΔG mínimo y medio, población) del `CLUSTERING HISTOGRAM`; RMSD al cluster y a la referencia de la `RMSD TABLE`; las 50 poses de los bloques `DOCKED: MODEL` | formato confirmado en los cuatro `.dlg` de controles; las líneas `DOCKED: ATOM` son PDBQT con 8 caracteres de prefijo, así que reusan el lector que ya existe |
| `.pdbqt` multi-modelo | poses y ΔG de `REMARK VINA RESULT` | ya lo lee QuEtool |
| `.pdbqt` / `.pdb` de receptor | átomos, residuos, hidrógenos polares | ya lo lee QuEtool |
| `.csv` cualquiera con columna de id | atributos del ligando | trivial, pero hay que resolver separador y coma decimal |

Lo que **no** está en el repo son los `.dlg` de la campaña: `.gitignore` los excluye junto a
los `.xml`, y sólo sobrevivieron los cuatro de los controles. Eso es lo que falta traer.

## 6. Las vistas

Cuatro, cada una contestando una pregunta distinta.

**Datos.** Arrastrás archivos y ves qué entró: cuántas corridas, qué receptores, qué
condiciones, qué quedó sin pareja, qué no se pudo leer y por qué. Es la vista menos vistosa
y la más importante: es donde se detecta que cargaste el receptor equivocado antes de sacar
una conclusión.

**Ranking.** Una fila por corrida: mejor ΔG, población del mejor cluster, eficiencia de
ligando, distancia al sitio. Ordenable y filtrable por condición, exportable a CSV con la
procedencia de cada número. Contesta "¿qué compuestos miro primero?".

**Complejo.** El visor 3D con el mapa de interacciones, igual que en QuEtool pero sobre el
receptor y la pose que elijas de lo que cargaste. Contesta "¿por qué este compuesto puntúa
así?".

**Correlaciones.** Elegís dos columnas cualesquiera —una de docking, otra de DFT, o las dos
de DFT— y salen la dispersión, Pearson, Spearman y el ajuste lineal con su intervalo.
Contesta "¿esto que calculé sirve para predecir algo?", que es la pregunta que convierte una
quimioteca en un modelo.

El dendrograma, la huella de contactos y el funnel plot del artefacto son buenas figuras y
deberían volver, pero después: las cuatro vistas de arriba son las que hacen falta para
decidir, y las otras tres son para publicar.

## 7. Qué se puede calcular en el navegador

Donde el artefacto delegó en Python, conviene medir antes de prometer.

- **Matriz de RMSD y clustering jerárquico** de las poses de un ligando: el artefacto tope
  en 90 poses. A ese tamaño es O(n²) en distancias y O(n³) en el enlace completo ingenuo:
  irrelevante, corre en milisegundos.
- **PCA** sobre la huella de contactos de 91 ligandos × ~300 residuos: también trivial, es
  una covarianza chica y unas pocas iteraciones de potencia.
- **UMAP** queda afuera de la primera versión, y no por costo. Con unas decenas de puntos
  sus ejes y sus distancias largas no significan nada, cosa que el propio artefacto admite
  en su texto de ayuda. PCA con ejes en ångström es la lectura defendible.
- **Análisis de interacciones** de la mejor pose de cada ligando: es lo único que puede
  doler, porque es el cálculo geométrico completo por cada pose. Hay que medirlo sobre los
  datos reales antes de decidir si corre al vuelo o en segundo plano con barra de progreso.
- **Dinámica molecular**: no. Ya lo medimos: GFN2 cuesta **1,02 s por paso** para 31 átomos,
  así que 1 ps son 17 minutos y no alcanza ni para ver un cambio conformacional. Y una MD del
  complejo necesitaría un campo de fuerzas para la proteína, que en el navegador no hay.

## 8. Trazabilidad

La carpeta es compartida y pasa por varias herramientas distintas, así que todo número que
el banco muestre tiene que poder rastrearse hasta el archivo del que salió. En concreto:
cada corrida guarda el nombre del archivo que la produjo, cada CSV exportado lleva esa
columna, y los criterios geométricos van escritos en la propia pantalla como ya están en
QuEtool. Nadie debería tener que leer el código para saber qué es un puente de hidrógeno
acá adentro.

## 9. Decisiones abiertas

1. **Ligandos sin DFT.** Los 17 `tdz*_e2` del ranking no tienen fila en la tabla DFT.
   ¿Entran al análisis marcados como incompletos, o se filtran por defecto?
2. **Qué es "la mejor pose"** por defecto en el ranking: el cluster de menor ΔG o el más
   poblado. Para A5I/7QCH tu propio registro dice que el bueno es el cluster 2 por población,
   y que el de menor energía es una pose con 1/50. El valor por defecto importa.
3. **Las cajas `_null`.** Son controles negativos y la mitad de las condiciones del ranking.
   ¿Vista aparte, o una columna más del ranking para comparar contra ellas?
4. **El canal BetaTools.** El esquema de nombres implica una segunda publicación del
   programa educativo —la de prueba— además de la estable. Técnicamente es barato (otra
   carpeta en el mismo repo, otra URL de Pages), pero hay que decidir si la cátedra ve las
   dos o sólo la estable.
5. **Dónde se publica.** QuEtool está en GitHub Pages. El banco maneja datos de una
   campaña sin publicar: ¿queda sólo local, o publicado pero vacío, cargando los archivos
   cada quien en su máquina? (Técnicamente lo segundo es seguro —nada sale del navegador—
   pero es una decisión tuya, no mía.)

## 10. Qué hace falta traer el miércoles

- Los `.dlg` (o `.xml`) de AutoDock-GPU de la campaña, aunque sea de una condición completa
  para empezar: 91 ligandos de una caja y una carga.
- Los receptores que vayan con esos `.dlg`, en PDBQT.
- El ligando cristalográfico de referencia de cada receptor, para fijar el sitio.
- `ranking.csv` y `docking_vs_dft.csv` actualizados, si cambiaron.

Con una condición completa alcanza para construir y validar las cuatro vistas; el resto entra
después sin tocar el código.
