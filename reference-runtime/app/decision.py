from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .hashing import hash_json, sha256_prefixed, canonical_json_bytes
from .models import (
    DecisionType,
    ExecutionDecision,
    ReasonCode,
    RuntimeMeta,
    DecisionProfileInfo,
    ApprovedCall,
)


@dataclass(frozen=True)
class RuntimeIdentity:
    name: str = "ecl-reference-runtime"
    version: str = "0.1.0"
    build: str = "local-dev"


def provenance_id_from_inputs(request_hash: str, profile_ref_hash: str, runtime_version: str) -> str:
    payload = {
        "request_hash": request_hash,
        "profile_ref_hash": profile_ref_hash,
        "runtime_version": runtime_version,
    }
    return sha256_prefixed(canonical_json_bytes(payload))


def provenance_id_from_request_hash(request_hash: str) -> str:
    # Deterministic provenance ID derived from request hash
    return "prov_" + request_hash.replace("sha256:", "")[:16]


def deny_decision(
    *,
    reason: ReasonCode,
    request_hash: str,
    profile_id: str,
    profile_version: str,
    profile_ref_hash: str,
    runtime: RuntimeIdentity,
) -> ExecutionDecision:
    return ExecutionDecision(
        decision_type=DecisionType.DENY,
        reason_code=reason,
        request_hash=request_hash,
        provenance_id=provenance_id_from_request_hash(request_hash),
        profile=DecisionProfileInfo(
            id=profile_id,
            version=profile_version,
            profile_ref_hash=profile_ref_hash,
        ),
        runtime=RuntimeMeta(name=runtime.name, version=runtime.version, build=runtime.build),
        approved_call=None,
    )


def allow_decision(
    *,
    request_hash: str,
    profile_id: str,
    profile_version: str,
    profile_ref_hash: str,
    tool_name: str,
    tool_args: Any,
    runtime: RuntimeIdentity,
) -> ExecutionDecision:
    return ExecutionDecision(
        decision_type=DecisionType.ALLOW,
        reason_code=ReasonCode.OK,
        request_hash=request_hash,
        provenance_id=provenance_id_from_request_hash(request_hash),
        profile=DecisionProfileInfo(
            id=profile_id,
            version=profile_version,
            profile_ref_hash=profile_ref_hash,
        ),
        runtime=RuntimeMeta(name=runtime.name, version=runtime.version, build=runtime.build),
        approved_call=ApprovedCall(tool_name=tool_name, tool_args=tool_args),
    )


def fallback_profile_ref_hash() -> str:
    # For cases where profile cannot even be loaded/parsed (e.g. malformed JSON request).
    # Deterministic constant to keep output stable.
    return sha256_prefixed(b"NO_PROFILE")
