import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

def load_routes(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def match_route(routes: dict[str, Any], method: str, path: str):
    key = f"{method.upper()} {path}"
    return routes.get(key)

class MockHandler(BaseHTTPRequestHandler):
    routes: dict[str, Any] = {}

    def _send(self, code: int, body: dict | list):
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        hit = match_route(self.routes, "GET", self.path)
        if hit is None:
            self._send(404, {"error": "not found"})
        else:
            self._send(200, hit)

    def log_message(self, format, *args):
        return

def serve(routes: dict[str, Any], host: str = "127.0.0.1", port: int = 0):
    handler = type("H", (MockHandler,), {"routes": routes})
    httpd = HTTPServer((host, port), handler)
    return httpd
