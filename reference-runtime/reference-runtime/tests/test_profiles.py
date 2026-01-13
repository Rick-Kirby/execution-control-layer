import json
import os

from fastapi.testclient import TestClient

from app.gate import create_app
from app.hashing import hash_json


def read_audit_lines(path: str):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def test_missing_profile_denies_profile_not_found(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.log"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))

    # Point profiles root somewhere empty
    empty_profiles = tmp_path / "profiles"
    empty_profiles.mkdir()
    monkeypatch.setenv("PROFILES_ROOT", str(empty_profiles))

    client = TestClient(create_app())

    req = {
        "request_id": "req1",
        "actor": {"principal_id": "user:1", "principal_type": "user", "attributes": {}},
        "tool": {"name": "email.send", "args": {"to": "a@example.com"}},
        "profile": {"id": "does_not_exist", "version": "1.0.0"},
        "context": {"snapshot": {"x": 1}, "snapshot_hash": hash_json({"x": 1})},
        "controls": {},
        "submitted_at": "2026-01-06T19:00:00Z",
    }

    resp = client.post("/v1/execute", content=json.dumps(req), headers={"content-type": "application/json"})
    assert resp.status_code == 200
    body = resp.json()

    assert body["decision_type"] == "DENY"
    assert body["reason_code"] == "PROFILE_NOT_FOUND"

    lines = read_audit_lines(str(audit_path))
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["reason_code"] == "PROFILE_NOT_FOUND"
