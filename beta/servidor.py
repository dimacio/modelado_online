"""Servidor local para la aplicacion.

A diferencia de `python -m http.server`, emite las cabeceras COOP y COEP, que son
las que habilitan SharedArrayBuffer. Sin ellas AutoDock Vina no arranca, porque usa
hilos. La parte de descriptores funciona igual con o sin cabeceras.
"""
import http.server, socketserver, sys

PUERTO = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      '.wasm': 'application/wasm', '.js': 'text/javascript',
                      '.mjs': 'text/javascript'}

    def end_headers(self):
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'credentialless')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write('  %s\n' % (fmt % args))

socketserver.TCPServer.allow_reuse_address = True
print(f'\n  Aplicacion en http://localhost:{PUERTO}/')
print('  Aislamiento de origen cruzado activado: el docking va a funcionar.')
print('  Para cortar: Ctrl+C\n')
with socketserver.TCPServer(('127.0.0.1', PUERTO), Handler) as s:
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print('\n  Servidor detenido.')
