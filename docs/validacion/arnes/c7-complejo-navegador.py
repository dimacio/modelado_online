# C7 — Prueba funcional de la pestaña Complejo con .dlg, en un Firefox de verdad.
# Requiere geckodriver escuchando en 4455 y la app servida por servidor.py en 8766,
# con los .dlg y el receptor en app/datos/. Maneja la app como un usuario: clics en
# las pestañas y archivos subidos por los input type=file.
# OJO: Firefox de snap no ve /tmp del sistema, y geckodriver ACUMULA archivos en un
# input multiple (el navegador real los reemplaza), por eso se limpia antes de subir.
import json, urllib.request, sys, time, os
B='http://127.0.0.1:4455'; D=os.path.expanduser('~/e2e-modelado/datos')
def req(m,p,d=None):
    r=urllib.request.Request(B+p,method=m,data=json.dumps(d).encode() if d is not None else None,
        headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(r,timeout=180) as f: return json.load(f)
    except urllib.error.HTTPError as e:
        raise SystemExit('HTTP '+str(e.code)+' en '+p+': '+e.read().decode()[:400])
s=req('POST','/session',{"capabilities":{"alwaysMatch":{"browserName":"firefox",
    "moz:firefoxOptions":{"args":["-headless"]}}}})
S=f"/session/{s['value']['sessionId']}"
def el(css):
    return req('POST',S+'/element',{"using":"css selector","value":css})['value']['element-6066-11e4-a52e-4f735466cecf']
def click(css): req('POST',S+f'/element/{el(css)}/click',{})
def limpiar(css): js("document.querySelector(arguments[0]).value=''",[css])
def subir(css,path): req('POST',S+f'/element/{el(css)}/value',{"text":path})
def js(code,args=None): return req('POST',S+'/execute/sync',{"script":code,"args":args or []})['value']
def txt(css): return req('GET',S+f'/element/{el(css)}/text')['value']
res=[]; 
def ok(n,c,d=''): res.append((n,bool(c),str(d))); print(('OK    ' if c else 'FALLA ')+n+((' — '+str(d)) if d else ''))
try:
    req('POST',S+'/url',{"url":"http://127.0.0.1:8766/index.html"}); time.sleep(7)
    click('#portadaEmpezar')
    click('#pestanas button[data-p="complejo"]'); time.sleep(1)
    ok('gancho de pruebas', js("return typeof window.__complejo")=='function')
    # receptor propio, por el input nuevo de la pestaña Complejo
    subir('#receptorArchivoC', D+'/6W63_3CLpro_receptor.pdbqt'); time.sleep(2)
    ok('receptor cargado desde Complejo','átomos' in txt('#receptorEstadoC'), txt('#receptorEstadoC'))
    # un .dlg enfocado: 50 corridas, 4 clusters
    limpiar('#poseArchivo'); subir('#poseArchivo', D+'/comp22.dlg'); time.sleep(6)
    e=js("return window.__complejo()")
    ok('50 poses leídas del .dlg', e['poses']==50, e['poses'])
    ok('4 clusters', len(e['clusters'])==4, len(e['clusters']))
    ok('interacciones medidas', len(e['inter'])>0, f"{len(e['inter'])} interacciones")
    ok('tabla de clusters con 4 filas', js("return document.querySelectorAll('#tablaClusters .filaCluster').length")==4)
    ok('cluster 1 con su población', e['clusters'][0]['n']==39, f"n={e['clusters'][0]['n']}, dG={e['clusters'][0]['mejor']}")
    ok('pie con corrida y cluster', 'cluster 1' in txt('#pieComplejo'), txt('#pieComplejo'))
    # modo Cluster
    click('#mCluster'); time.sleep(4); e=js("return window.__complejo()")
    ok('modo Cluster superpone los 39 miembros', e['modelos']==1+39, f"{e['modelos']} modelos")
    # modo Representantes
    click('#mRepres'); time.sleep(4); e=js("return window.__complejo()")
    ok('modo Representantes: 1 por cluster', e['modelos']==1+4, f"{e['modelos']} modelos")
    ok('leyenda con los clusters', 'cl 4' in txt('#leyenda').lower(), txt('#leyenda').replace('\n',' ')[:120])
    # flechas
    click('#mPose'); time.sleep(3)
    v0=js("return +document.getElementById('poseSel').value")
    click('#poseSig'); time.sleep(3)
    ok('flecha avanza de pose', js("return +document.getElementById('poseSel').value")==v0+1)
    # docking ciego: 100 corridas, 35 clusters, y clic en una fila
    limpiar('#poseArchivo'); subir('#poseArchivo', D+'/ciego35.dlg'); time.sleep(7); e=js("return window.__complejo()")
    ok('ciego: 100 poses y 35 clusters', e['poses']==100 and len(e['clusters'])==35,
       f"{e['poses']} poses, {len(e['clusters'])} clusters")
    ok('avisa que las poses no tocan al receptor', 'no se tocan' in txt('#complejoEstado'), txt('#complejoEstado'))
    js("[...document.querySelectorAll('#tablaClusters .filaCluster')].find(t=>t.dataset.rank==='3').click()")
    time.sleep(4); e=js("return window.__complejo()")
    ok('clic en una fila salta a la mejor pose de ese cluster', e['clusterDeLaPose']==3, f"cluster {e['clusterDeLaPose']}")
    # dos archivos a la vez → selector de ligando
    limpiar('#poseArchivo')
    subir('#poseArchivo', D+'/comp22.dlg\n'+D+'/ciego35.dlg'); time.sleep(8); e=js("return window.__complejo()")
    ok('dos ligandos cargados', len(e['conjuntos'])==2, json.dumps(e['conjuntos']))
    ok('selector de ligando visible', js("return !document.getElementById('ligSel').hidden"))
    js("const s=document.getElementById('ligSel'); s.value='1'; s.dispatchEvent(new Event('change'))")
    time.sleep(5); e=js("return window.__complejo()")
    ok('cambiar de ligando cambia las poses', e['cual']==1 and e['poses']==100, f"cual={e['cual']}, poses={e['poses']}")
    # sin errores en consola
    errs=js("return (window.__errores||[])")
finally:
    try: req('DELETE',S)
    except Exception: pass
mal=sum(1 for _,c,_ in res if not c)
print(f"\n{len(res)-mal} OK, {mal} fallas")
sys.exit(1 if mal else 0)
