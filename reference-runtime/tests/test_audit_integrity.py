import json
import pathlib
import hashlib

from fastapi.testclient import TestClient

from app.gate import create_app
from app.hashing import canonical_json_bytes, hash_json

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILES_DIR = str(REPO_ROOT / "profiles")


def _read_lines(path: pathlib.Path):
    if not path.exists():
        return []
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _record_hash(record: dict) -> str:
    # Must match app.audit.append_audit_record
    r = dict(record)
    integrity = dict(r["integrity"])
    integrity["record_hash"] = ""
    r["integrity"] = integrity
    h = hashlib.sha256(canonical_json_bytes(r)).hexdigest()
    return "sha256:" + h


def test_audit_hash_chain_links_and_verifies(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.log"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))
    monkeypatch.setenv("PROFILES_ROOT", PROFILES_DIR)

    client = TestClient(create_app())

    base_req = {
        "actor": {"principal_id": "user:1", "principal_type": "user", "attributes": {}},
        "profile": {"id": "example", "version": "1.0.0"},
        "context": {"snapshot": {"x": 1}, "snapshot_hash": hash_json({"x": 1})},
        "controls": {},
    }

    r1 = dict(base_req)
    r1["request_id"] = "audit_1"
    r1["tool"] = {"name": "db.drop_all", "args": {"sure": True}}

    r2 = dict(base_req)
    r2["request_id"] = "audit_2"
    r2["tool"] = {"name": "email.send", "args": {"to": "bob@example.com", "subject": "hi"}}

    client.post("/v1/execute", content=json.dumps(r1), headers={"content-type": "application/json"})
    client.post("/v1/execute", content=json.dumps(r2), headers={"content-type": "application/json"})

    lines = _read_lines(audit_path)
    assert len(lines) == 2

    rec1 = json.loads(lines[0])
    rec2 = json.loads(lines[1])

    # seq must increment deterministically
    assert rec1["seq"] == 0
    assert rec2["seq"] == 1

    # chain must link
    assert rec2["integrity"]["prev_hash"] == rec1["integrity"]["record_hash"]

    # record_hash must verify (tamper-evident)
    assert rec1["integrity"]["record_hash"] == _record_hash(rec1)
    assert rec2["integrity"]["record_hash"] == _record_hash(rec2)
