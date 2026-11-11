# C7 — Poses y clusters de AutoDock en la pestaña Complejo

Qué se agregó, qué se verificó y con qué datos. Fecha: 2026-11-11.

Esto vive en **BetaTools** (`beta/`), el canal de pruebas, no en QuEtool (`app/`). Pasa a
la estable cuando se haya usado en serio contra una campaña completa.

## Qué se agregó

La pestaña Complejo leía un solo archivo: el PDBQT de poses que escribe Vina. Ahora lee
también el `.dlg` de **AutoDock 4 / AutoDock-GPU**, con su agrupamiento por RMSD, y permite
cargar varios archivos a la vez.

1. **Lector de `.dlg`** (`leerDLG`). Las líneas de coordenadas vienen con el prefijo
   `DOCKED: `; sacado el prefijo son PDBQT común, así que el resto de la pestaña —el
   dibujo y la medición de interacciones— no se tocó. De cada `MODEL` sale el número de
   corrida y su ΔG.
2. **Clusters leídos, no recalculados.** Salen de la `RMSD TABLE` que escribe el propio
   AutoDock con su tolerancia de rms. La app no reagrupa nada: muestra lo que decidió el
   programa que hizo el docking. De ahí salen ΔG del mejor miembro, ΔG medio, población y
   la RMSD de cada corrida contra el jefe de su cluster.
3. **Tabla de clusters** con el histograma de población, al lado de la de interacciones.
   Un clic en una fila lleva a la mejor pose de ese cluster. Exporta CSV, y el cluster
   entero como PDBQT multi-modelo.
4. **Tres modos de vista**: `Pose` (la de siempre), `Cluster` (la pose elegida más el
   resto de su cluster en palos finos: se ve de un vistazo si el cluster es compacto o
   está desparramado) y `Representantes` (la mejor pose de cada cluster, diez colores y
   el resto en gris).
5. **Varios ligandos a la vez.** El input acepta selección múltiple y aparece un selector
   para pasar de uno a otro: sirve para comparar el mismo ligando entre cajas o entre
   cargas.
6. **Receptor propio desde la misma pestaña**, porque el de la pestaña Docking no tiene
   por qué ser el de estas poses.
7. **Aviso de receptor equivocado.** Si una pose no da ninguna interacción, se mide su
   distancia al átomo más cercano del receptor y, si pasa de 6 Å, se avisa que no se
   tocan. Es el síntoma de cargar un receptor que no corresponde, o de una caja puesta en
   otro lado.

8. **RMSD contra el ligando cristalográfico**, cuando la corrida llevó `--xraylfile`. El
   número **no se recalcula**: es la columna *Reference RMSD* de la `RMSD TABLE`, que
   AutoDock calcula **corrigiendo por simetría** (recalcularla átomo contra átomo infla el
   valor en ligandos con anillos simétricos: X77/6W63 da 1,42 Å por nombre de átomo contra
   0,85 Å con la corrección). Si el `.dlg` no declara ligando de referencia, la columna mide
   contra la geometría de entrada y no significa nada, así que no se muestra.
9. **El ligando cristalográfico dibujado**, sacado del propio `.dlg`: la sección
   `XRAY-LIGAND-PDBQT` trae sus coordenadas, así que no hace falta cargar ningún archivo.
10. **El cluster se elige pesando energía y población**, no energía sola. El ranking de
    AutoDock ordena por ΔG, y por eso su cluster 1 puede ser una pose que apareció una vez.
    El criterio del proyecto —población ≥ 10 % de las corridas y, entre los que pasan, el de
    menor ΔG— es el que la pestaña marca y el que preselecciona al abrir el archivo.

El encuadre sigue a las poses: si están todas en el mismo bolsillo se acerca, y si andan
desparramadas —el caso del docking ciego— abre a toda la proteína.

## Criterios y resultados

| Paso | Qué se verificó | Criterio | Resultado |
|---|---|---|---|
| C7.1 | Lectura de una campaña entera de `.dlg` | en cada archivo: poses con ΔG, suma de clusters = número de corridas, y cada cluster con sus miembros indexados | **1553/1553 archivos, 0 fallas → ACEPTA** |
| C7.2 | Que el mapa de interacciones no haya cambiado | las once poses de C4 contra 2B6A, idénticas fila por fila a los CSV de C5 | **12/12 idénticos → ACEPTA** |
| C7.3 | La pestaña en un navegador real | las 32 comprobaciones de `c7-complejo-navegador.py` | **32/32 → ACEPTA** |
| C7.4 | RMSD al cristal y elección de cluster en los cuatro controles de redocking | reproducir la `RMSD TABLE` del `.dlg` y que el criterio elija el cluster correcto | **7/7 → ACEPTA** |

Los datos de C7.1 son los 1553 `.dlg` de la campaña de `dimacio/quimioteca-gaussian`
(`autodock/gpu/results/`, 20 condiciones: 6LU7, 6W63 y 7QCH/7LBR, cajas enfocada, ciega,
catalítica y nula, cargas Gasteiger y CM5), más los `_deep` de 500 corridas. No se copian
acá por tamaño (409 MB); el arnés toma la carpeta como argumento.

## Un bug que encontró el barrido

La primera versión del lector daba por perdidas filas de la `RMSD TABLE` en 8 de los 1553
archivos, todos del control nulo `7QCH_PLpro_null_gasteiger`, y uno de ellos se quedaba
sin ningún cluster. La causa: **AutoDock escribe las energías positivas con signo `+`**
(`+0.42`, `+33.23`) y la expresión regular sólo aceptaba el `-`. En los controles nulos,
donde el ligando no tiene dónde apoyarse, las energías positivas son la regla y no la
excepción. Corregido; el barrido pasó a 1553/1553.

Vale como advertencia general: probar el lector con los dockings que salieron bien no
alcanza, porque justamente los casos degenerados son los que traen los formatos raros.

## El caso que justifica pesar la población

`A5I/7QCH` es el ejemplo: el **mínimo de energía** es el cluster 1, con **1 de 50 corridas**
y a **4,27 Å** del cristal. La pose correcta —**1,00 Å**— es el cluster 2, con 49 de 50. Con
el criterio del proyecto la pestaña abre directamente en el cluster 2; ordenando por energía
sola, abriría en la pose equivocada. Los otros tres controles dan lo mismo por los dos
caminos, porque su cluster 1 ya es el poblado.

| Control | Criterio (población + ΔG) | Energía sola | RMSD al cristal |
|---|---|---|---|
| A5I / 7QCH | cluster 2 — 98 % | cluster 1 — 2 % | **1,00** vs 4,27 |
| X77 / 6W63 | cluster 1 — 100 % | igual | 0,88 |
| XT7 / 7LBR | cluster 1 — 30 % | igual | 1,95 |

## Una diferencia con los controles ya publicados

Los `.txt` de `gpu/salida_adt/controls/` (generados por `cluster_rmsd.py`) informan, por
cluster, el **mejor RMSD de cualquiera de sus miembros**. La pestaña informa el de la pose
de **menor ΔG**, que es la que uno reportaría, y entre paréntesis el mínimo del cluster
cuando difieren. Donde más se nota es en XT7/7LBR: el publicado es **1,30 Å** —el mejor
miembro, la corrida 46— mientras que la pose que gana por energía, la corrida 39, está a
**1,95 Å**. El control sigue aceptando (≤ 2 Å), pero con menos margen del que sugiere la
tabla. Son dos preguntas distintas: «¿el cluster contiene una pose buena?» y «¿la pose que
elegiría reproduce el cristal?».

## Cómo reproducirlo

```bash
# C7.1 — barrido del lector sobre la campaña
node docs/validacion/arnes/c7-barrido-dlg.mjs beta/index.html <carpeta con los .dlg>

# C7.2 — regresión del mapa de interacciones
node docs/validacion/arnes/c7-regresion-c5.mjs beta/index.html docs/validacion/datos

# C7.4 — RMSD al cristal y criterio de cluster, contra los controles del proyecto
node docs/validacion/arnes/c7-controles-cristal.mjs beta/index.html \
     <carpeta controls/results> <un .dlg de producción>

# C7.3 — la pestaña en Firefox
#   copiar los .dlg y el receptor a beta/datos/, y en dos terminales:
python3 beta/servidor.py 8766
geckodriver --port 4455
python3 docs/validacion/arnes/c7-complejo-navegador.py
```
