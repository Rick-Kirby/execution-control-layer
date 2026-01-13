import json
import os
import pathlib

from fastapi.testclient import TestClient

from app.gate import create_app
from app.hashing import hash_json

# Ensure PROFILES_ROOT resolves deterministically regardless of pytest cwd.
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILES_DIR = str(REPO_ROOT / "profiles")


def test_tool_not_allowed(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.log"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))
    monkeypatch.setenv("PROFILES_ROOT", PROFILES_DIR)

    client = TestClient(create_app())

    req = {
        "request_id": "req_tool_not_allowed",
        "actor": {"principal_id": "user:1", "principal_type": "user", "attributes": {}},
        "tool": {"name": "db.drop_all", "args": {"sure": True}},
        "profile": {"id": "example", "version": "1.0.0"},
        "context": {"snapshot": {"x": 1}, "snapshot_hash": hash_json({"x": 1})},
        "controls": {},
    }

    resp = client.post("/v1/execute", content=json.dumps(req), headers={"content-type": "application/json"})
    body = resp.json()
    assert body["decision_type"] == "DENY"
    assert body["reason_code"] == "TOOL_NOT_ALLOWED"


def test_allow_email_send_when_constraints_met(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.log"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))
    monkeypatch.setenv("PROFILES_ROOT", PROFILES_DIR)

    client = TestClient(create_app())

    req = {
        "request_id": "req_allow",
        "actor": {"principal_id": "user:1", "principal_type": "user", "attributes": {}},
        "tool": {"name": "email.send", "args": {"to": "bob@example.com", "subject": "hi"}},
        "profile": {"id": "example", "version": "1.0.0"},
        "context": {"snapshot": {"x": 1}, "snapshot_hash": hash_json({"x": 1})},
        "controls": {},
    }

    resp = client.post("/v1/execute", content=json.dumps(req), headers={"content-type": "application/json"})
    body = resp.json()
    assert body["decision_type"] == "ALLOW"
    assert body["reason_code"] == "OK"
    assert body["approved_call"]["tool_name"] == "email.send"
    assert body["approved_call"]["tool_args"]["to"] == "bob@example.com"


def test_control_required_for_storage_put(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.log"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))
    monkeypatch.setenv("PROFILES_ROOT", PROFILES_DIR)

    client = TestClient(create_app())

    req = {
        "request_id": "req_control",
        "actor": {"principal_id": "user:1", "principal_type": "user", "attributes": {}},
        "tool": {"name": "storage.put", "args": {"key": "a", "value": "b"}},
        "profile": {"id": "example", "version": "1.0.0"},
        "context": {"snapshot": {"x": 1}, "snapshot_hash": hash_json({"x": 1})},
        "controls": {},
    }

    resp = client.post("/v1/execute", content=json.dumps(req), headers={"content-type": "application/json"})
    body = resp.json()
    assert body["decision_type"] == "DENY"
    assert body["reason_code"] == "CONTROL_REQUIRED"


def test_constraint_violation_email_domain(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.log"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))
    monkeypatch.setenv("PROFILES_ROOT", PROFILES_DIR)

    client = TestClient(create_app())

    req = {
        "request_id": "req_bad_domain",
        "actor": {"principal_id": "user:1", "principal_type": "user", "attributes": {}},
        "tool": {"name": "email.send", "args": {"to": "bob@gmail.com", "subject": "hi"}},
        "profile": {"id": "example", "version": "1.0.0"},
        "context": {"snapshot": {"x": 1}, "snapshot_hash": hash_json({"x": 1})},
        "controls": {},
    }

    resp = client.post("/v1/execute", content=json.dumps(req), headers={"content-type": "application/json"})
    body = resp.json()
    assert body["decision_type"] == "DENY"
    assert body["reason_code"] == "CONSTRAINT_VIOLATION"
