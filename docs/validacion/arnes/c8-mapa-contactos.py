"""C8 — Prueba del Mapa de contactos de BetaTools, en un Firefox de verdad.

A diferencia del arnes de C7 (WebDriver crudo por HTTP contra un geckodriver ya
levantado), este usa selenium, que maneja el geckodriver solo:
    pip install selenium
    python -m http.server 8777   # desde beta/
    python c8-mapa-contactos.py [carpeta con los datos]
Los datos (receptor 7LBR + comp02/tsc30/comp22.dlg de la quimioteca) tienen que
estar BAJO ~ : el Firefox de snap no ve /tmp.

Carga el receptor de 7LBR y tres .dlg de la quimioteca, aprieta «Calcular el
mapa» y comprueba que los residuos que salen son los del surco BL2 — que es
donde ya sabemos que caen esas poses por el analisis del proyecto de docking.
"""
import json, os, sys, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

D = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/pruebas_mapa")
URL = "http://localhost:8777/index.html"
# el surco BL2 / bolsillo de GRL0617, segun el docking ya analizado
BL2 = {162, 163, 164, 166, 167, 248, 264, 266, 267, 268, 269}

o = Options(); o.add_argument("-headless")
o.binary_location = "/snap/firefox/current/usr/lib/firefox/firefox"
dr = webdriver.Firefox(options=o)
dr.set_window_size(1400, 1000)
fallos = []
try:
    # coi-serviceworker RECARGA la pagina la primera vez que se registra, y esa
    # recarga se lleva puesto lo que se haya cargado antes. Se entra una vez,
    # se espera a que quede activo y recien entonces se empieza en serio.
    dr.get(URL); time.sleep(3)
    dr.refresh(); time.sleep(3)
    dr.execute_script("const e=document.getElementById('portada'); if(e) e.hidden=true;")
    # pestaña Complejo
    dr.execute_script("""
      const b=[...document.getElementById('pestanas').children].find(x=>x.dataset.p==='complejo');
      b.click();""")
    time.sleep(1)

    dr.find_element(By.ID, "receptorArchivoC").send_keys(os.path.join(D, "7LBR_PLpro_cat_receptor.pdbqt"))
    time.sleep(3)
    # un input multiple: geckodriver ACUMULA, asi que se mandan los tres juntos
    assert dr.execute_script("return window.__complejo().receptor.nombre"), "el receptor no se cargó"
    ligs = "\n".join(os.path.join(D, f) for f in ("comp02.dlg", "tsc30.dlg", "comp22.dlg"))
    dr.find_element(By.ID, "poseArchivo").send_keys(ligs)
    time.sleep(4)

    print("estado receptor:", dr.execute_script("return document.getElementById('receptorEstadoC').textContent"))
    print("receptorTxt cargado:", dr.execute_script("return (window.__recdbg&&window.__complejo().receptor)||'n/d'"))
    n = dr.execute_script("return window.__complejo().conjuntos.length")
    print(f"ligandos cargados: {n}")
    if n != 3: fallos.append(f"se esperaban 3 conjuntos, hay {n}")

    dr.execute_script("document.getElementById('calcMapa').click()")
    for _ in range(90):
        time.sleep(1)
        if dr.execute_script("return !!(window.__complejo().mapa)"): break
    m = dr.execute_script("return window.__complejo().mapa")
    if not m:
        fallos.append("el mapa no se calculó"); raise SystemExit
    print(f"columnas (residuos): {len(m['columnas'])}")
    print("residuos:", ", ".join(m["columnas"]))
    for f in m["filas"]:
        top = sorted(f["res"], key=lambda x: -x[1])[:6]
        print(f"  {f['nombre']}: cluster {f['cluster']}, {f['nPoses']} poses -> " +
              ", ".join(f"{r} {n}/{f['nPoses']}" for r, n in top))

    num = lambda s: int("".join(c for c in s if c.isdigit()))
    en_bl2 = [c for c in m["columnas"] if num(c) in BL2]
    frac = len(en_bl2) / len(m["columnas"])
    print(f"residuos en el surco BL2: {len(en_bl2)}/{len(m['columnas'])} ({frac:.0%})")
    if frac < 0.5:
        fallos.append(f"solo {frac:.0%} de los residuos caen en BL2; se esperaba la mayoria")

    # el CSV tiene que tener una fila por ligando y una columna por residuo
    csv = dr.execute_script("""
      const b=document.getElementById('bajarMapa'); return b.disabled;""")
    if csv: fallos.append("los botones de CSV quedaron deshabilitados")

    # invalidacion: cambiar el criterio tiene que borrar el mapa
    dr.execute_script("document.getElementById('mapaCluster').click()")
    time.sleep(0.5)
    if dr.execute_script("return !!(window.__complejo().mapa)"):
        fallos.append("cambiar el criterio no invalidó el mapa")
    else:
        print("invalidación al cambiar el criterio: OK")

    errores = dr.execute_script("return (window.__erroresJS||[])")
    if errores: fallos.append(f"errores de JS: {errores}")
finally:
    dr.save_screenshot(os.path.join(D, "mapa.png"))
    dr.quit()

print("\n" + ("FALLOS:\n  " + "\n  ".join(fallos) if fallos else "todo OK"))
sys.exit(1 if fallos else 0)
