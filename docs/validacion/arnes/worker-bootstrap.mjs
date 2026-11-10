// Bootstrap: emula el entorno de un worker del navegador sobre node:worker_threads y
// carga vina.worker.js (el script de hilos de Webina). Es el eslabón que permite que
// Vina cree sus pthreads en Node igual que lo hace en el navegador.
import { parentPort, workerData } from 'node:worker_threads';
import { pathToFileURL } from 'node:url';

globalThis.self = globalThis;

let onmessage = null;
Object.defineProperty(globalThis, 'onmessage', {
  get: () => onmessage,
  set: (f) => { onmessage = f; },
});

globalThis.postMessage = (data, transfer) => {
  if (transfer && transfer.length) parentPort.postMessage(data, transfer);
  else parentPort.postMessage(data);
};

parentPort.on('message', (data) => { if (onmessage) onmessage({ data }); });

await import(pathToFileURL(workerData.workerPath).href);
