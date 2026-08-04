#!/usr/bin/env python3
"""Sirve esta carpeta para instalar el Voucher térmico en el celular.

Uso:   python3 serve.py [puerto]      (por defecto 8080)

Registra el MIME de .webmanifest, que es lo que suele romper la instalación
con `python3 -m http.server`.
"""
import functools
import http.server
import mimetypes
import os
import socket
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
ROOT = os.path.dirname(os.path.abspath(__file__))

mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/html; charset=utf-8", ".html")


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # El caché lo maneja el service worker, no el navegador.
        self.send_header("Cache-Control", "no-store")
        self.send_header("Service-Worker-Allowed", "/")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s  %s\n" % (self.address_string(), fmt % args))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    handler = functools.partial(Handler, directory=ROOT)
    with Server(("0.0.0.0", PORT), handler) as srv:
        print("Sirviendo %s" % ROOT)
        print("  http://localhost:%d          <- contexto seguro (usar con adb reverse)" % PORT)
        print("  http://%s:%d   <- desde el celular en la misma red" % (lan_ip(), PORT))
        print("Ctrl+C para detener.")
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nDetenido.")
