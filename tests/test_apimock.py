import json
import urllib.error
import urllib.request
from pathlib import Path
from apimock.core import load_routes, match_route, serve, MockHandler

def test_load_routes(tmp_path):
    p = tmp_path / "r.json"
    p.write_text('{"GET /hi": {"ok": true}}', encoding="utf-8")
    assert load_routes(p)["GET /hi"]["ok"]

def test_match():
    r = {"GET /users": [1]}
    assert match_route(r, "get", "/users") == [1]

def test_serve_request():
    routes = {"GET /ping": {"pong": 1}}
    httpd = serve(routes, port=0)
    port = httpd.server_address[1]
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/ping", timeout=2
        ) as resp:
            body = json.loads(resp.read())
        assert body["pong"] == 1
    finally:
        httpd.shutdown()
        httpd.server_close()

def test_404():
    httpd = serve({}, port=0)
    port = httpd.server_address[1]
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/nope", timeout=2)
        assert False
    except urllib.error.HTTPError as e:
        assert e.code == 404
    finally:
        httpd.shutdown()
        httpd.server_close()

def test_handler_class():
    assert MockHandler.routes == {} or isinstance(MockHandler.routes, dict)
