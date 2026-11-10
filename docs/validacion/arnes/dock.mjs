// Validación C4 — driver de docking con Webina (AutoDock Vina 1.2.3 compilado a
// WebAssembly) ejecutado directamente desde Node.js, replicando la llamada exacta
// que hace QuEtool (app/index.html, pestaña Docking, ver sección "docking").
//
// Uso:  node dock.mjs <nombre_ligando_sin_extension> [carpeta_salida]
// Ej.:  node dock.mjs GFA                     (escribe en Validacion-Webina/poses/)
//       node dock.mjs GFA poses
//
// Diferencias documentadas respecto de la app en navegador:
//  * cpu = 1: en Node este build de Webina no tiene soporte de workers del
//    navegador; la propia app recomienda núcleos = 1 en máquinas chicas.
//  * El .wasm se pasa como wasmBinary (leído con fs) en vez de locateFile.
//  * Todo lo demás (preRun con FS.writeFile, callMain con los mismos
//    argumentos --receptor/--ligand/--out, lectura de /ligand_out.pdbqt en
//    onExit, sin --seed ni --num_modes) es idéntico a la app.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { Worker } from 'node:worker_threads';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

// Diagnóstico opcional: WEBINA_DEBUG=1 node dock.mjs <ligando>
const verbose = process.env.WEBINA_DEBUG === '1';
const log = (...a) => { if (verbose) console.error('[webina]', ...a); };

const HERE = path.dirname(fileURLToPath(import.meta.url));   // carpeta del arnés
// Carpeta de materiales: por defecto un nivel arriba (carpeta de trabajo del arnés);
// se puede apuntar a otra con MATERIALES_DIR (útil para la copia archivada en el repo).
const PROJ = process.env.MATERIALES_DIR ? path.resolve(process.env.MATERIALES_DIR) : path.resolve(HERE, '..');
// Motor Webina: la copia de trabajo trae lib/Webina/; la copia archivada en el repo
// usa app/lib/Webina/ del propio repo.
const WEBINA_DIR = existsSync(path.join(HERE, 'lib', 'Webina'))
  ? path.join(HERE, 'lib', 'Webina')
  : path.resolve(HERE, '..', 'app', 'lib', 'Webina');

const [, , ligName, outDir] = process.argv;
if (!ligName) { console.error('Uso: node dock.mjs <ligando> [salida]'); process.exit(2); }
const destino = outDir ? path.resolve(PROJ, outDir) : path.join(HERE, 'poses');

// ── conf.txt del proyecto (misma caja que usa el TP y la validación nativa) ──
const conf = {};
for (const ln of readFileSync(path.join(PROJ, 'conf.txt'), 'utf8').split('\n')) {
  const l = ln.split('#')[0].trim();
  if (l.includes('=')) { const [k, v] = l.split('='); conf[k.trim()] = v.trim(); }
}
const params = {
  center_x: +conf.center_x, center_y: +conf.center_y, center_z: +conf.center_z,
  size_x: +conf.size_x, size_y: +conf.size_y, size_z: +conf.size_z,
  exhaustiveness: +conf.exhaustiveness,   // 10, como el TP
  energy_range: +conf.energy_range,       // 3, como el TP
  cpu: 1,                                 // ver nota al principio
};

// Shims defensivos para correr el build (pensado para navegador) bajo Node.
if (typeof globalThis.self === 'undefined') globalThis.self = globalThis;

// Webina es un build de Emscripten con pthreads para navegador: al arrancar pre-reserva
// workers (`new Worker('vina.worker.js')`) y Vina crea sus hilos de búsqueda con
// pthread_create/join. Node no tiene la API Worker del navegador, así que se tiende un
// puente a node:worker_threads: cada "Worker de navegador" es un worker de Node que corre
// worker-bootstrap.mjs, el cual emula el entorno de worker (self, postMessage, onmessage)
// y carga el vina.worker.js de Webina. Así los hilos de Vina ejecutan de verdad y el
// pthread_join del hilo principal se destraba igual que en el navegador.
globalThis.Worker = class BrowserWorkerBridge {
  constructor(url) {
    log('worker puente creado para:', url);
    this.onmessage = null;
    this.onerror = null;
    this.pthread_ptr = 0;
    const bootstrap = new URL('./worker-bootstrap.mjs', import.meta.url);
    this._w = new Worker(bootstrap, { workerData: { workerPath: String(url) } });
    this._w.on('message', (data) => { if (this.onmessage) this.onmessage({ data }); });
    this._w.on('error', (err) => {
      if (this.onerror) this.onerror({ filename: '', lineno: 0, message: err && err.message });
      else throw err;
    });
  }
  postMessage(data, transfer) {
    if (transfer && transfer.length) this._w.postMessage(data, transfer);
    else this._w.postMessage(data);
  }
  terminate() { return this._w.terminate(); }
};

const receptorTxt = readFileSync(path.join(PROJ, 'Receptor', '2B6A_receptor.pdbqt'), 'utf8');
const ligando = readFileSync(path.join(PROJ, 'Ligandos', ligName + '.pdbqt'), 'utf8');
const wasmBinary = readFileSync(path.join(WEBINA_DIR, 'vina.wasm'));

const WEBINA = (await import(pathToFileURL(path.join(WEBINA_DIR, 'vina.1.0.5.js')).href)).default;
log('módulo vina.1.0.5.js importado');

const t0 = Date.now();
let stdout = '';
let stdoutErr = '';
const { pose, out, code } = await new Promise((resolve, reject) => {
  const wd = setTimeout(() => log('WATCHDOG 240 s: la promesa sigue pendiente'), 240000);
  let iniciado = null;
  log('construyendo el módulo WEBINA');
  const mod = new WEBINA({
    noInitialRun: true,
    wasmBinary,
    locateFile: (p) => { log('locateFile:', p); return path.join(WEBINA_DIR, p); },
    monitorRunDependencies: (n) => log('dependencias restantes:', n),
    preRun: [function (This) {
      log('preRun: escribiendo receptor y ligando en el FS virtual');
      This.FS.writeFile('/receptor.pdbqt', receptorTxt);
      This.FS.writeFile('/ligand.pdbqt', ligando);
      iniciado = This;
      log('preRun ok:', receptorTxt.length, 'y', ligando.length, 'caracteres escritos');
    }],
    print: (t) => { stdout += t + '\n'; },
    printErr: (t) => { stdoutErr += t + '\n'; },
    onAbort: (what) => { log('onAbort:', what); clearTimeout(wd); reject(new Error('Vina abortó: ' + what)); },
    onExit: (exitCode) => {
      log('onExit:', exitCode);
      clearTimeout(wd);
      let p = '';
      try { p = iniciado.FS.readFile('/ligand_out.pdbqt', { encoding: 'utf8' }); } catch {}
      resolve({ pose: p, out: stdout, code: exitCode });
    },
  });
  Promise.resolve(mod).then((m) => (m && m.ready) ? m.ready : m).then((m) => {
    const args = [];
    for (const [k, v] of Object.entries(params)) args.push('--' + k, String(v));
    args.push('--receptor', '/receptor.pdbqt', '--ligand', '/ligand.pdbqt', '--out', '/ligand_out.pdbqt');
    // callMain le hace unshift(thisProgram) al array: copiar antes para la llamada directa
    const argsDirecto = args.slice();
    log('ready resuelto; callMain con', args.join(' '));
    log('exports del wasm:', Object.keys(m.asm).join(' '));
    const ret = m.callMain(args);
    log('callMain retornó:', ret);
    try { m.checkMailbox(); } catch (e) { log('checkMailbox:', e && e.message); }
    // En Node el despacho proxied del main no se procesa (en el navegador lo resuelve el
    // event loop). Si el archivo de salida no apareció, se llama al entry point de Vina
    // directamente —la misma función que invoca el proxy— construyendo argv a mano.
    let yaCorrio = false;
    try { yaCorrio = m.FS.readFile('/ligand_out.pdbqt', { encoding: 'utf8' }).length > 0; } catch {}
    if (!yaCorrio) {
      const L = (typeof m._main === 'function') ? m._main
        : (typeof m.asm.L === 'function') ? m.asm.L : null;
      const stackAlloc = (typeof m.asm.stackAlloc === 'function') ? m.asm.stackAlloc
        : (typeof m.asm.ca === 'function') ? m.asm.ca : null;
      if (L && stackAlloc) {
        const strs = ['vina', ...argsDirecto];
        const mem = new Uint8Array(m.wasmMemory.buffer);
        const u32 = new Uint32Array(m.wasmMemory.buffer);
        const te = new TextEncoder();
        const ptrs = [];
        for (const s of strs) {
          const p = stackAlloc(s.length + 1);
          mem.set(te.encode(s), p); mem[p + s.length] = 0;
          ptrs.push(p);
        }
        const argvPtr = stackAlloc((ptrs.length + 1) * 4);
        ptrs.forEach((p, i) => { u32[(argvPtr + i * 4) >> 2] = p; });
        u32[(argvPtr + ptrs.length * 4) >> 2] = 0;
        log('corriendo _main directamente con', strs.length, 'argumentos:', JSON.stringify(strs));
        let retMain;
        try { retMain = L(ptrs.length, argvPtr); } catch (e) {
          if (typeof e === 'number') {
            const u32x = new Uint32Array(m.wasmMemory.buffer);
            const u8x = new Uint8Array(m.wasmMemory.buffer);
            try {
              const excPtr = e - 24;
              const typeInfo = u32x[excPtr >> 2];
              const namePtr = u32x[(typeInfo + 4) >> 2];
              let s = '', i = namePtr;
              while (u8x[i]) s += String.fromCharCode(u8x[i++]);
              log('tipo de excepción C++:', s);
            } catch (e2) { log('no se pudo decodificar la excepción:', e2 && e2.message); }
          } else {
            log('excepción en _main:', e);
          }
          log('stderr de Vina:', JSON.stringify(stdoutErr.slice(0, 2000)));
          retMain = 'exception';
        }
        log('_main retornó:', retMain);
      } else {
        log('no hay entry point directo (L, stackAlloc):', !!L, !!stackAlloc);
      }
    }
    // En Node onExit no se dispara: callMain mantiene vivo el runtime y el ExitStatus
    // se traga en handleException, así que el módulo nunca "sale". La app en el
    // navegador lee el archivo en onExit; acá se lee del mismo FS apenas main termina.
    let p = '';
    try { p = m.FS.readFile('/ligand_out.pdbqt', { encoding: 'utf8' }); } catch {}
    log('pose leída del FS:', p.length, 'caracteres');
    clearTimeout(wd);
    resolve({ pose: p, out: stdout, code: ret });
  }).catch((e) => { log('reject:', e && e.stack ? e.stack : e); clearTimeout(wd); reject(e); });
});

const segundos = ((Date.now() - t0) / 1000).toFixed(1);

// Mismo parseo que la app: líneas REMARK VINA RESULT → [ΔG, rmsd_inf, rmsd_sup]
const filas = pose.split('\n').filter((l) => l.includes('VINA RESULT'))
  .map((l) => l.trim().split(/\s+/).slice(3).map(Number));

if (!filas.length) {
  const res = { ligando: ligName, ok: false, salidaVina: out, salidaVinaErr: stdoutErr, segundos };
  writeFileSync(path.join(destino, ligName + '.json'), JSON.stringify(res, null, 2));
  console.error(JSON.stringify(res));
  setTimeout(() => process.exit(1), 100);
}

mkdirSync(destino, { recursive: true });
writeFileSync(path.join(destino, ligName + '_webina.pdbqt'), pose);

const res = {
  ligando: ligName,
  ok: true,
  motor: 'Webina 1.0.5 (Vina 1.2.3 en WASM), archivos de modelado_online@ff964ce',
  exitCode: code,
  dG_kcal_mol: filas[0][0],
  rmsd_inf: filas[0][1],
  rmsd_sup: filas[0][2],
  modos: filas.length,
  todos_los_modos: filas.map((f) => Number(f[0].toFixed(3))),
  parametros: params,
  segundos,
};
writeFileSync(path.join(destino, ligName + '.json'), JSON.stringify(res, null, 2));
console.log(JSON.stringify(res));
setTimeout(() => process.exit(0), 100);
