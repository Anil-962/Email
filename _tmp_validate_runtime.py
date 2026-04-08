from fastapi.testclient import TestClient

from server.main import app


client = TestClient(app)

endpoints = [
    ("GET", "/health"),
    ("GET", "/metadata"),
    ("GET", "/schema"),
    ("POST", "/mcp"),
    ("POST", "/reset"),
    ("POST", "/step"),
    ("GET", "/state"),
]

for method, path in endpoints:
    if method == "GET":
        res = client.get(path)
    else:
        payload = {"message": "ping"} if path == "/step" else {}
        res = client.post(path, json=payload)
    print(method, path, res.status_code)
