import json
import pathlib
import hashlib

from fastapi.testclient import TestClient

from app.gate import create_app
from app.hashing import hash_json

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILES_DIR = str(REPO_ROOT / "profiles")


def _post(client: TestClient, req: dict) -> dict:
    return client.post(
        "/v1/execute",
        content=json.dumps(req),
        headers={"content-type": "application/json"},
    ).json()


def _decision_fingerprint(d: dict) -> dict:
    # Fields that must be stable for determinism
    return {
        "decision_type": d["decision_type"],
        "reason_code": d["reason_code"],
        "request_hash": d["request_hash"],
        "provenance_id": d["provenance_id"],
        "profile": d["profile"],               # includes profile_ref_hash
        "approved_call": d.get("approved_call"),
        "runtime": d["runtime"],
    }


def test_same_request_same_decision(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.log"))
    monkeypatch.setenv("PROFILES_ROOT", PROFILES_DIR)

    client = TestClient(create_app())

    req = {
        "request_id": "req_det_1",
        "actor": {"principal_id": "user:1", "principal_type": "user", "attributes": {}},
        "tool": {"name": "email.send", "args": {"to": "bob@example.com", "subject": "hi"}},
        "profile": {"id": "example", "version": "1.0.0"},
        "context": {"snapshot": {"x": 1}, "snapshot_hash": hash_json({"x": 1})},
        "controls": {},
    }

    d1 = _post(client, req)
    d2 = _post(client, req)

    assert _decision_fingerprint(d1) == _decision_fingerprint(d2)


def test_canonicalization_key_order_irrelevant(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.log"))
    monkeypatch.setenv("PROFILES_ROOT", PROFILES_DIR)

    client = TestClient(create_app())

    req_a = {
        "request_id": "req_det_2",
        "actor": {"principal_id": "user:1", "principal_type": "user", "attributes": {}},
        "tool": {"name": "email.send", "args": {"subject": "hi", "to": "bob@example.com"}},
        "profile": {"id": "example", "version": "1.0.0"},
        "context": {"snapshot": {"x": 1}, "snapshot_hash": hash_json({"x": 1})},
        "controls": {},
    }

    # Same semantics, different key order across the whole request
    req_b = {
        "profile": {"version": "1.0.0", "id": "example"},
        "tool": {"args": {"to": "bob@example.com", "subject": "hi"}, "name": "email.send"},
        "actor": {"attributes": {}, "principal_type": "user", "principal_id": "user:1"},
        "controls": {},
        "context": {"snapshot_hash": hash_json({"x": 1}), "snapshot": {"x": 1}},
        "request_id": "req_det_2",
    }

    d1 = _post(client, req_a)
    d2 = _post(client, req_b)

    assert _decision_fingerprint(d1) == _decision_fingerprint(d2)


def test_profile_ref_hash_binds_to_exact_profile_bytes(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.log"))
    monkeypatch.setenv("PROFILES_ROOT", PROFILES_DIR)

    client = TestClient(create_app())

    req = {
        "request_id": "req_det_3",
        "actor": {"principal_id": "user:1", "principal_type": "user", "attributes": {}},
        "tool": {"name": "email.send", "args": {"to": "bob@example.com", "subject": "hi"}},
        "profile": {"id": "example", "version": "1.0.0"},
        "context": {"snapshot": {"x": 1}, "snapshot_hash": hash_json({"x": 1})},
        "controls": {},
    }

    d = _post(client, req)

    profile_path = REPO_ROOT / "profiles" / "example" / "1.0.0.json"
    raw = profile_path.read_bytes()
    expected = "sha256:" + hashlib.sha256(raw).hexdigest()

    assert d["profile"]["profile_ref_hash"] == expected
