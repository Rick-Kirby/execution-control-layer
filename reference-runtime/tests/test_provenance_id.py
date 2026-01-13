import json
import pathlib

from fastapi.testclient import TestClient

from app.gate import create_app
from app.hashing import hash_json

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILES_DIR = str(REPO_ROOT / "profiles")


def test_provenance_id_deterministic(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.log"))
    monkeypatch.setenv("PROFILES_ROOT", PROFILES_DIR)

    client = TestClient(create_app())

    req = {
        "request_id": "prov_1",
        "actor": {"principal_id": "user:1", "principal_type": "user", "attributes": {}},
        "tool": {"name": "email.send", "args": {"to": "bob@example.com", "subject": "hi"}},
        "profile": {"id": "example", "version": "1.0.0"},
        "context": {"snapshot": {"x": 1}, "snapshot_hash": hash_json({"x": 1})},
        "controls": {},
    }

    d1 = client.post("/v1/execute", content=json.dumps(req), headers={"content-type": "application/json"}).json()
    d2 = client.post("/v1/execute", content=json.dumps(req), headers={"content-type": "application/json"}).json()

    assert d1["provenance_id"] == d2["provenance_id"]
