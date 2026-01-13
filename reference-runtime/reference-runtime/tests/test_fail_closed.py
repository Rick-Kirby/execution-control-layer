import json
import os

import pytest
from fastapi.testclient import TestClient

from app.gate import create_app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.log"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))
    app = create_app()
    return TestClient(app)


def read_audit_lines(path: str):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def test_malformed_json_denies_and_writes_audit(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.log"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))

    client = TestClient(create_app())

    # Malformed JSON (missing closing brace)
    resp = client.post("/v1/execute", data='{"bad": true', headers={"content-type": "application/json"})
    assert resp.status_code == 200

    body = resp.json()
    assert body["decision_type"] == "DENY"
    assert body["reason_code"] == "REQUEST_PARSE_ERROR"
    assert body["request_hash"].startswith("sha256:")
    assert body["provenance_id"].startswith("prov_")

    lines = read_audit_lines(str(audit_path))
    assert len(lines) == 1

    rec = json.loads(lines[0])
    assert rec["decision_type"] == "DENY"
    assert rec["reason_code"] == "REQUEST_PARSE_ERROR"
    assert rec["request_hash"] == body["request_hash"]
