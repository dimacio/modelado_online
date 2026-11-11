// Prueba funcional de la app con las novedades del TP remoto, vía CDP sobre Edge headless.
// Corre contra servidor.py (COOP/COEP): valida selector de la serie, CSV de descriptores
// (import y export con descarga real), receptor 2B6A con caja del TP, docking completo de
// NVP, descargas de poses/salida, complejo con interacciones y carga de poses de archivo.
import { readFileSync, existsSync, mkdirSync, rmSync } from 'node:fs';

const DL = 'C:\\Users\\dimas\\c2-work\\descargas';
if (existsSync(DL)) rmSync(DL, { recursive: true, force: true });
mkdirSync(DL, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const chequeos = [];
const check = (nombre, ok, detalle = '') => {
  chequeos.push({ nombre, ok, detalle });
  console.log(`${ok ? 'OK ' : 'FALLA'}  ${nombre}${detalle ? ' — ' + detalle : ''}`);
};

async function main() {
  let page = null;
  for (let i = 0; i < 30 && !page; i++) {
    try {
      const list = await fetch('http://127.0.0.1:9222/json/list').then((r) => r.json());
      page = list.find((t) => t.type === 'page');
      if (!page) page = await fetch('http://127.0.0.1:9222/json/new?about:blank', { method: 'PUT' }).then((r) => r.json());
    } catch { await sleep(1000); }
  }
  if (!page) throw new Error('no hay target de Edge');

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((ok, mal) => { ws.onopen = ok; ws.onerror = mal; });
  let id = 0; const pend = new Map();
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.mal(new Error(m.error.message)) : p.ok(m.result); }
  };
  const enviar = (method, params = {}) => new Promise((ok, mal) => { const i = ++id; pend.set(i, { ok, mal }); ws.send(JSON.stringify({ id: i, method, params })); });
  const evaluar = async (expr) => {
    const r = await enviar('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error('eval: ' + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
    return r.result?.value;
  };

  await enviar('Runtime.enable');
  await enviar('Page.enable');
  try { await enviar('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: DL, eventsEnabled: false }); } catch {}

  await enviar('Page.navigate', { url: 'http://127.0.0.1:8000/' });
  for (let i = 0; i < 240; i++) {
    await sleep(500);
    const s = (await evaluar(`document.getElementById('estado')?.textContent || ''`)) || '';
    if (s.startsWith('Listo')) break;
  }
  check('app arranca (estado Listo)', ((await evaluar(`document.getElementById('estado')?.textContent || ''`)) || '').startsWith('Listo'));
  check('crossOriginIsolated (COOP/COEP)', await evaluar('self.crossOriginIsolated') === true);

  // 1) selector de la serie
  await evaluar(`document.getElementById('serieTP').value = '4'; document.getElementById('serieTP').dispatchEvent(new Event('change', { bubbles: true }))`);
  const smi = await evaluar(`document.getElementById('smiles').value`);
  check('selector carga SMILES de NVP', smi.startsWith('Cc1ccnc2c1'));

  // 2) descriptores: calcular y exportar CSV (descarga real)
  await evaluar(`document.getElementById('calcular').click(); true`);
  for (let i = 0; i < 120; i++) {
    await sleep(500);
    const s = (await evaluar(`document.getElementById('estado')?.textContent || ''`)) || '';
    if (s.startsWith('Listo') || s.startsWith('Error')) break;
  }
  const filasSerie = await evaluar(`document.querySelectorAll('#tabla tbody tr').length`);
  check('descriptores calculados (fila en Serie)', filasSerie === 1, `filas=${filasSerie}`);
  await evaluar(`document.getElementById('descargar').click(); true`);
  await sleep(1500);
  const csvBajado = existsSync(DL + '\\descriptores.csv');
  check('descarga CSV de descriptores', csvBajado);
  if (csvBajado) {
    const txt = readFileSync(DL + '\\descriptores.csv', 'utf8');
    check('CSV exportado contiene NVP', txt.includes('Cc1ccnc2c1') && txt.includes('clogP'));
  }

  // 3) importar CSV (roundtrip con el archivo recién descargado)
  const csvCont = readFileSync(DL + '\\descriptores.csv', 'utf8').replace(/\\/g, '\\\\').replace(/`/g, '\\`');
  await evaluar(`(function(){ const f = new File([\`${csvCont}\`], 'descriptores.csv', {type:'text/csv'});
    Object.defineProperty(document.getElementById('serieArchivo'), 'files', { value: [f] });
    document.getElementById('serieArchivo').dispatchEvent(new Event('change')); return true; })()`);
  await sleep(1000);
  const estadoImp = (await evaluar(`document.getElementById('estado')?.textContent || ''`)) || '';
  check('import CSV restaura la serie', estadoImp.startsWith('Serie cargada'), estadoImp);

  // 4) docking: 2B6A + caja del TP
  await evaluar(`[...document.querySelectorAll('#pestanas button')].find((b) => b.dataset.p === 'docking').click(); true`);
  for (let i = 0; i < 240; i++) {
    await sleep(500);
    const s = (await evaluar(`document.getElementById('dockEstado')?.textContent || ''`)) || '';
    if (s === 'Listo.' || s.startsWith('No se pudo')) break;
  }
  const dockEstadoTxt = await evaluar(`document.getElementById('dockEstado')?.textContent || ''`);
  check('docking preparado (OpenBabel + Vina)', dockEstadoTxt === 'Listo.', dockEstadoTxt);
  await evaluar(`document.getElementById('receptor').value = 'datos/2B6A_receptor.pdbqt'; document.getElementById('receptor').dispatchEvent(new Event('change')); true`);
  await sleep(4000);
  const cx = await evaluar(`document.getElementById('cx').value`);
  const ex = await evaluar(`document.getElementById('ex').value`);
  const recEstado = await evaluar(`document.getElementById('receptorEstado')?.textContent || ''`);
  check('2B6A carga y aplica caja del TP', cx === '145.876' && ex === '10' && /líneas/.test(recEstado), `cx=${cx} ex=${ex} ${recEstado}`);

  // 5) docking real de NVP (cpu 1 para que sea rápido)
  await evaluar(`document.getElementById('cpu').value = '1'; document.getElementById('dockear').click(); true`);
  for (let i = 0; i < 480; i++) {
    await sleep(500);
    const s = (await evaluar(`document.getElementById('dockEstado')?.textContent || ''`)) || '';
    if (s.startsWith('Listo en') || s.startsWith('Error')) break;
  }
  const dockFin = (await evaluar(`document.getElementById('dockEstado')?.textContent || ''`)) || '';
  const nPoses = await evaluar(`document.querySelectorAll('#poses table tbody tr').length`);
  check('docking de NVP termina con poses', dockFin.startsWith('Listo en') && nPoses > 0, `${dockFin} (${nPoses} poses)`);
  const salida = await evaluar(`document.getElementById('vinaSalida')?.textContent || ''`);
  check('log de Vina presente', salida.length > 10);

  await evaluar(`document.getElementById('bajarSalida').click(); true`);
  await sleep(1500);
  check('descarga salida completa (params + log)', existsSync(DL + '\\vina_salida.txt'));
  await evaluar(`document.getElementById('bajarPose').click(); true`);
  await sleep(1500);
  check('descarga PDBQT de poses', existsSync(DL + '\\poses.pdbqt'));

  // 6) complejo: interacciones + descarga CSV + carga de poses de archivo
  await evaluar(`[...document.querySelectorAll('#pestanas button')].find((b) => b.dataset.p === 'complejo').click(); true`);
  for (let i = 0; i < 120; i++) {
    await sleep(500);
    const s = (await evaluar(`document.getElementById('complejoEstado')?.textContent || ''`)) || '';
    if (s === 'Listo.') break;
  }
  const nInter = await evaluar(`document.querySelectorAll('#tablaInter table tbody tr').length`);
  check('complejo: tabla de interacciones poblada', nInter > 0, `${nInter} interacciones`);
  await evaluar(`document.getElementById('bajarInter').click(); true`);
  await sleep(1500);
  check('descarga CSV de interacciones', existsSync(DL + '\\interacciones.csv'));

  // carga de poses desde archivo (T50_webina.pdbqt local)
  const poseTxt = readFileSync('C:\\Users\\dimas\\c2-work\\poses\\T50_webina.pdbqt', 'utf8').replace(/\\/g, '\\\\').replace(/`/g, '\\`');
  await evaluar(`(function(){ const f = new File([\`${poseTxt}\`], 'T50_webina.pdbqt', {type:'text/plain'});
    Object.defineProperty(document.getElementById('poseArchivo'), 'files', { value: [f] });
    document.getElementById('poseArchivo').dispatchEvent(new Event('change')); return true; })()`);
  await sleep(2000);
  const nOpciones = await evaluar(`document.querySelectorAll('#poseSel option').length`);
  check('carga de poses desde archivo', nOpciones > 0, `${nOpciones} poses en el selector`);

  const todas = chequeos.filter((c) => c.ok).length;
  console.log(`\n== ${todas}/${chequeos.length} chequeos OK ==`);
  const malas = chequeos.filter((c) => !c.ok);
  process.exit(malas.length ? 1 : 0);
}

main().catch((e) => { console.error('FALLO:', (e && e.stack) || e); process.exit(1); });
