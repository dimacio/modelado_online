# Librerías con licencia copyleft

Estos dos componentes **no** son BSD ni Apache como el resto del stack, y viajan con su licencia:

| Carpeta | Origen | Licencia |
|---|---|---|
| `Webina/` | [durrantlab/webina](https://github.com/durrantlab/webina), AutoDock Vina 1.2.3 a WebAssembly | Apache-2.0 |
| `openbabel/` | OpenBabel compilado a WebAssembly, tomado del bundle de Webina | **GPL-2.0** |

OpenBabel es GPL-2.0. Distribuirlo junto al resto hace que el conjunto quede sujeto a GPL.
Webina evita eso corriendo su conversor en un iframe aparte, "a distancia de brazo". Si querés
conservar una licencia permisiva para la aplicación, hay que hacer lo mismo o reemplazar la
conversión a PDBQT por otra implementación.

Decisión pendiente, anotada para no descubrirla tarde.
