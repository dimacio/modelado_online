// Diagnóstico del arranque de vina.1.0.5.js bajo Node. No dockea nada:
// sólo carga el módulo y registra cada etapa para ver dónde se detiene.
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const WEBINA_DIR = path.join(HERE, 'lib', 'Webina');

if (typeof globalThis.self === 'undefined') globalThis.self = globalThis;
if (typeof globalThis.Worker === 'undefined') {
  globalThis.Worker = class DummyWorker {
    constructor(url) { console.log('[dummy] creado:', url); this.onmessage = null; this.onerror = null; this.pthread_ptr = 0; }
    postMessage(msg) {
      console.log('[dummy] postMessage cmd =', msg && msg.cmd);
      if (msg && msg.cmd === 'load') {
        queueMicrotask(() => {
          console.log('[dummy] responde loaded, onmessage seteado =', !!this.onmessage);
          if (this.onmessage) this.onmessage({ data: { cmd: 'loaded' } });
        });
      }
    }
    terminate() { console.log('[dummy] terminate'); }
  };
}

console.log('[1] importando vina.1.0.5.js');
const WEBINA = (await import(pathToFileURL(path.join(WEBINA_DIR, 'vina.1.0.5.js')).href)).default;
console.log('[2] importado, tipo:', typeof WEBINA);

const wasmBinary = readFileSync(path.join(WEBINA_DIR, 'vina.wasm'));

const mod = new WEBINA({
  noInitialRun: true,
  wasmBinary,
  locateFile: (p) => { console.log('[locateFile]', p); return path.join(WEBINA_DIR, p); },
  print: (t) => console.log('[out]', String(t).trim()),
  printErr: (t) => console.log('[err]', String(t).trim()),
  onAbort: (w) => console.log('[ABORT]', w),
  setStatus: (s) => console.log('[status]', s),
  monitorRunDependencies: (n) => console.log('[deps restantes]', n),
  onRuntimeInitialized: () => console.log('[runtime inicializado]'),
  onExit: (c) => console.log('[exit]', c),
});
console.log('[3] construido; es Promise:', mod instanceof Promise);
mod.then(
  (m) => { console.log('[4] ready RESUELTO con:', typeof m); process.exit(0); },
  (e) => { console.log('[4] ready RECHAZADO:', e && e.stack ? e.stack : e); process.exit(1); },
);
setTimeout(() => console.log('[5] 30 s sin resolver'), 30000);
setTimeout(() => process.exit(2), 40000);
