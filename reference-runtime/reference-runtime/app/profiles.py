from __future__ import annotations

import os
from typing import Tuple

from pydantic import ValidationError

from .hashing import sha256_prefixed
from .models import ExecutionProfile, ReasonCode


def _profiles_root() -> str:
    return os.getenv("PROFILES_ROOT", "profiles")


def profile_path(profile_id: str, profile_version: str) -> str:
    # profiles/{id}/{version}.json
    root = _profiles_root()
    return os.path.join(root, profile_id, f"{profile_version}.json")


def load_profile(profile_id: str, profile_version: str) -> Tuple[ExecutionProfile, str]:
    """
    Returns (profile_model, profile_ref_hash).
    Fail closed:
      - missing file => PROFILE_NOT_FOUND
      - parse/validation error => PROFILE_PARSE_ERROR
    """
    path = profile_path(profile_id, profile_version)
    if not os.path.exists(path):
        raise RuntimeError(ReasonCode.PROFILE_NOT_FOUND.value)

    try:
        with open(path, "rb") as f:
            raw = f.read()
    except Exception:
        # treat as not found / inaccessible
        raise RuntimeError(ReasonCode.PROFILE_NOT_FOUND.value)

    # Hash the exact bytes as the immutable profile ref
    profile_ref_hash = sha256_prefixed(raw)

    try:
        profile = ExecutionProfile.model_validate_json(raw.decode("utf-8"))
    except Exception:
        raise RuntimeError(ReasonCode.PROFILE_PARSE_ERROR.value)

    # Extra sanity: profile header must match requested id/version (fail closed)
    if profile.profile_id != profile_id or profile.profile_version != profile_version:
        raise RuntimeError(ReasonCode.PROFILE_PARSE_ERROR.value)

    return profile, profile_ref_hash
