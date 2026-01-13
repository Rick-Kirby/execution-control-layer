from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json_bytes(obj: Any) -> bytes:
    """
    Deterministic JSON canonicalization (minimal).
    - sort keys
    - no whitespace
    - UTF-8
    """
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_prefixed(data: bytes) -> str:
    return f"sha256:{sha256_hex(data)}"


def hash_json(obj: Any) -> str:
    return sha256_prefixed(canonical_json_bytes(obj))
