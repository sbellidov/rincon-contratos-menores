import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = "docs"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"--- Portal de Transparencia: Rincón de la Victoria ---")
    print(f"Servidor iniciado en http://localhost:{PORT}")
    print("Presiona Ctrl+C para detener el servidor.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
