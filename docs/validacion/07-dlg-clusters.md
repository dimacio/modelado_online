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

El encuadre sigue a las poses: si están todas en el mismo bolsillo se acerca, y si andan
desparramadas —el caso del docking ciego— abre a toda la proteína.

## Criterios y resultados

| Paso | Qué se verificó | Criterio | Resultado |
|---|---|---|---|
| C7.1 | Lectura de una campaña entera de `.dlg` | en cada archivo: poses con ΔG, suma de clusters = número de corridas, y cada cluster con sus miembros indexados | **1553/1553 archivos, 0 fallas → ACEPTA** |
| C7.2 | Que el mapa de interacciones no haya cambiado | las once poses de C4 contra 2B6A, idénticas fila por fila a los CSV de C5 | **12/12 idénticos → ACEPTA** |
| C7.3 | La pestaña en un navegador real | las 18 comprobaciones de `c7-complejo-navegador.py` | **18/18 → ACEPTA** |

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

## Cómo reproducirlo

```bash
# C7.1 — barrido del lector sobre la campaña
node docs/validacion/arnes/c7-barrido-dlg.mjs beta/index.html <carpeta con los .dlg>

# C7.2 — regresión del mapa de interacciones
node docs/validacion/arnes/c7-regresion-c5.mjs beta/index.html docs/validacion/datos

# C7.3 — la pestaña en Firefox
#   copiar los .dlg y el receptor a beta/datos/, y en dos terminales:
python3 beta/servidor.py 8766
geckodriver --port 4455
python3 docs/validacion/arnes/c7-complejo-navegador.py
```
