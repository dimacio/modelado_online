// Driver de la app QuEtool (pestaña Descriptores) vía CDP sobre Edge headless.
// Sin Playwright: usa el WebSocket nativo de Node y el endpoint /json de DevTools.
// Para cada SMILES de smiles_nnrti.json: lo carga en la app, pulsa Calcular, espera
// "Listo", y captura la grilla de resultados + el estado del SCF de GFN2.
import { writeFileSync, readFileSync } from 'node:fs';

const smis = JSON.parse(readFileSync('smiles_nnrti.json', 'utf8'));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  let page = null;
  for (let i = 0; i < 30 && !page; i++) {
    try {
      const list = await fetch('http://127.0.0.1:9222/json/list').then((r) => r.json());
      page = list.find((t) => t.type === 'page');
      if (!page) page = await fetch('http://127.0.0.1:9222/json/new?about:blank', { method: 'PUT' }).then((r) => r.json());
    } catch { await sleep(1000); }
  }
  if (!page) throw new Error('no se pudo obtener un target de Edge');
  console.log('target:', page.url);

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((ok, mal) => { ws.onopen = ok; ws.onerror = mal; });
  let id = 0;
  const pend = new Map();
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) {
      const p = pend.get(m.id); pend.delete(m.id);
      m.error ? p.mal(new Error(m.error.message)) : p.ok(m.result);
    }
  };
  const enviar = (method, params = {}) => new Promise((ok, mal) => {
    const i = ++id; pend.set(i, { ok, mal }); ws.send(JSON.stringify({ id: i, method, params }));
  });
  const evaluar = async (expr) => {
    const r = await enviar('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error('eval: ' + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
    return r.result?.value;
  };

  await enviar('Runtime.enable');
  await enviar('Page.enable');
  await enviar('Page.navigate', { url: 'http://127.0.0.1:8765/index.html' });

  let listo = false;
  for (let i = 0; i < 240; i++) {
    await sleep(500);
    const s = (await evaluar(`document.getElementById('estado')?.textContent || ''`)) || '';
    if (s.startsWith('Listo')) { listo = true; break; }
    if (s.startsWith('No se pudieron cargar')) break;
  }
  if (!listo) {
    const s = await evaluar(`document.getElementById('estado')?.textContent || ''`);
    throw new Error('la app no arrancó: ' + s);
  }
  console.log('app lista');

  const filas = [];
  for (const [nombre, smi] of Object.entries(smis)) {
    await evaluar(`document.getElementById('smiles').value = ${JSON.stringify(smi)}`);
    await evaluar(`document.getElementById('calcular').click(); true`);
    let estado = '';
    for (let i = 0; i < 120; i++) {
      await sleep(500);
      estado = (await evaluar(`document.getElementById('estado')?.textContent || ''`)) || '';
      if (estado.startsWith('Listo') || estado.startsWith('Error')) break;
    }
    const celdas = (await evaluar(`[...document.querySelectorAll('#resultado .celda .v')].map((e) => e.textContent.trim())`)) || [];
    const tiempos = (await evaluar(`document.getElementById('tiempos')?.textContent || ''`)) || '';
    const fila = { nombre, smiles: smi, estado, celdas, tiempos };
    filas.push(fila);
    console.log(JSON.stringify(fila));
  }
  writeFileSync('descriptores_quetool_nnrti.json', JSON.stringify(filas, null, 2));
  console.log('LISTO');
  process.exit(0);
}

main().catch((e) => { console.error('FALLO:', (e && e.stack) || e); process.exit(1); });
