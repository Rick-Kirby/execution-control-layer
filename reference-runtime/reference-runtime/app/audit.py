from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .hashing import canonical_json_bytes, sha256_prefixed


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class AuditAppendResult:
    seq: int
    prev_hash: str
    record_hash: str


def _audit_path() -> str:
    """
    Resolve AUDIT_LOG_PATH, expanding {pid} if present.
    """
    raw = os.getenv("AUDIT_LOG_PATH", "audit.log")
    if "{pid}" in raw:
        raw = raw.replace("{pid}", str(os.getpid()))
    return raw


def _tail_last_record(path: str) -> Optional[Dict[str, Any]]:
    """
    Read only the last JSONL line (best-effort).
    O(file size) worst-case but done once per writer init.
    """
    if not os.path.exists(path):
        return None

    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            if f.tell() == 0:
                return None

            pos = f.tell() - 1
            while pos > 0:
                f.seek(pos)
                if f.read(1) == b"\n":
                    break
                pos -= 1

            if pos == 0:
                f.seek(0)

            line = f.readline().decode("utf-8").strip()
            if not line:
                return None
            return json.loads(line)
    except Exception:
        return None


class AuditWriter:
    """
    Single-process audit writer.

    Properties:
    - Deterministic append-only hash chain
    - O(1) per append
    - Thread-safe within process
    """
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._lock = threading.Lock()

        last = _tail_last_record(path)
        if last:
            self._seq = int(last.get("seq", 0)) + 1
            self._last_hash = last.get("integrity", {}).get("record_hash", "sha256:GENESIS")
        else:
            self._seq = 0
            self._last_hash = "sha256:GENESIS"

        self._fh = open(path, "ab", buffering=0)

    def append(self, record: Dict[str, Any]) -> AuditAppendResult:
        with self._lock:
            seq = self._seq
            prev_hash = self._last_hash

            record = dict(record)
            record["seq"] = seq
            record["integrity"] = {"prev_hash": prev_hash, "record_hash": ""}

            record_for_hash = dict(record)
            integrity = dict(record_for_hash["integrity"])
            integrity["record_hash"] = ""
            record_for_hash["integrity"] = integrity

            record_hash = sha256_prefixed(canonical_json_bytes(record_for_hash))
            record["integrity"]["record_hash"] = record_hash

            line = canonical_json_bytes(record) + b"\n"
            self._fh.write(line)
            self._fh.flush()

            self._seq += 1
            self._last_hash = record_hash

            return AuditAppendResult(seq=seq, prev_hash=prev_hash, record_hash=record_hash)


# One writer per resolved path
_WRITERS: Dict[str, AuditWriter] = {}
_WRITERS_LOCK = threading.Lock()


def _get_writer(path: str) -> AuditWriter:
    with _WRITERS_LOCK:
        w = _WRITERS.get(path)
        if w is None:
            w = AuditWriter(path)
            _WRITERS[path] = w
        return w


def append_audit_record(record: Dict[str, Any]) -> AuditAppendResult:
    path = _audit_path()
    writer = _get_writer(path)
    return writer.append(record)
