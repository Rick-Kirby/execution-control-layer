from __future__ import annotations
import anyio

import json
from typing import Any, Dict
from .enforce import find_tool_permit, require_controls, enforce_constraints
from .decision import allow_decision

from fastapi import FastAPI, Request
from pydantic import ValidationError
from .profiles import load_profile
from .decision import provenance_id_from_inputs

from .audit import append_audit_record, utc_now_iso
from .decision import RuntimeIdentity, deny_decision, fallback_profile_ref_hash
from .hashing import sha256_prefixed, hash_json, canonical_json_bytes
from .models import ExecutionRequest, ReasonCode, DecisionType


def create_app() -> FastAPI:
    app = FastAPI(title="ECL Reference Runtime", version="0.1.0")

    runtime = RuntimeIdentity()

    @app.post("/v1/execute")
    async def execute(request: Request) -> Dict[str, Any]:
        received_at = utc_now_iso()
        raw = await request.body()

        # Defaults for cases where parsing fails
        profile_id = "UNKNOWN"
        profile_version = "UNKNOWN"
        profile_ref_hash = fallback_profile_ref_hash()
        request_id = "UNKNOWN"

        try:
            # We parse JSON ourselves to ensure malformed JSON becomes a deterministic DENY
            try:
                obj = json.loads(raw.decode("utf-8"))
            except Exception:
                req_hash = sha256_prefixed(raw)
                decision = deny_decision(
                    reason=ReasonCode.REQUEST_PARSE_ERROR,
                    request_hash=req_hash,
                    profile_id=profile_id,
                    profile_version=profile_version,
                    profile_ref_hash=profile_ref_hash,
                    runtime=runtime,
                )

                decided_at = utc_now_iso()
                record = _audit_record_from_denied(
                    request_id=request_id,
                    request_hash=req_hash,
                    profile_id=profile_id,
                    profile_version=profile_version,
                    profile_ref_hash=profile_ref_hash,
                    decision_type=decision.decision_type,
                    reason_code=decision.reason_code.value,
                    runtime=decision.runtime.model_dump(),
                    received_at=received_at,
                    decided_at=decided_at,
                )

                # MUST attempt audit write; failure modes handled later (fail-closed)
                await anyio.to_thread.run_sync(append_audit_record, record)

                return decision.model_dump()

            # Schema validation (strict)
            try:
                req = ExecutionRequest.model_validate(obj)
            except ValidationError:
                req_hash = sha256_prefixed(canonical_json_bytes(obj))
                decision = deny_decision(
                    reason=ReasonCode.REQUEST_SCHEMA_INVALID,
                    request_hash=req_hash,
                    profile_id=profile_id,
                    profile_version=profile_version,
                    profile_ref_hash=profile_ref_hash,
                    runtime=runtime,
                )

                decided_at = utc_now_iso()
                record = _audit_record_from_denied(
                    request_id=request_id,
                    request_hash=req_hash,
                    profile_id=profile_id,
                    profile_version=profile_version,
                    profile_ref_hash=profile_ref_hash,
                    decision_type=decision.decision_type,
                    reason_code=decision.reason_code.value,
                    runtime=decision.runtime.model_dump(),
                    received_at=received_at,
                    decided_at=decided_at,
                )
                await anyio.to_thread.run_sync(append_audit_record, record)
                return decision.model_dump()

            # From here on, we have a valid request shape
            request_id = req.request_id
            profile_id = req.profile.id
            profile_version = req.profile.version

            # Deterministic hashes
            req_hash = hash_json(req.model_dump())

            # Context snapshot integrity check (fail closed)
            computed_ctx = hash_json(req.context.snapshot)
            if req.context.snapshot_hash != computed_ctx:
                decision = deny_decision(
                    reason=ReasonCode.CTX_HASH_MISMATCH,
                    request_hash=req_hash,
                    profile_id=profile_id,
                    profile_version=profile_version,
                    profile_ref_hash=profile_ref_hash,
                    runtime=runtime,
                )
                decided_at = utc_now_iso()
                record = _audit_record_from_denied(
                    request_id=request_id,
                    request_hash=req_hash,
                    profile_id=profile_id,
                    profile_version=profile_version,
                    profile_ref_hash=profile_ref_hash,
                    decision_type=decision.decision_type,
                    reason_code=decision.reason_code.value,
                    runtime=decision.runtime.model_dump(),
                    received_at=received_at,
                    decided_at=decided_at,
                )
                await anyio.to_thread.run_sync(append_audit_record, record)
                return decision.model_dump()

                        # Load profile (fail closed)
                        
            try:
                profile_model, profile_ref_hash = load_profile(profile_id, profile_version)
            except RuntimeError as e:
                reason_str = str(e.args[0]) if e.args else ReasonCode.PROFILE_PARSE_ERROR.value
                reason = (
                    ReasonCode(reason_str)
                    if reason_str in ReasonCode._value2member_map_
                    else ReasonCode.PROFILE_PARSE_ERROR
                )

                decision = deny_decision(
                    reason=reason,
                    request_hash=req_hash,
                    profile_id=profile_id,
                    profile_version=profile_version,
                    profile_ref_hash=profile_ref_hash,
                    runtime=runtime,
                )

                decided_at = utc_now_iso()
                record = _audit_record_from_denied(
                    request_id=request_id,
                    request_hash=req_hash,
                    profile_id=profile_id,
                    profile_version=profile_version,
                    profile_ref_hash=profile_ref_hash,
                    decision_type=decision.decision_type,
                    reason_code=decision.reason_code.value,
                    runtime=decision.runtime.model_dump(),
                    received_at=received_at,
                    decided_at=decided_at,
                )
                await anyio.to_thread.run_sync(append_audit_record, record)
                return decision.model_dump()

            # Enforce allowlist + controls + constraints
            permit = find_tool_permit(profile_model, req.tool.name)
            if permit is None:
                decision = deny_decision(
                    reason=ReasonCode.TOOL_NOT_ALLOWED,
                    request_hash=req_hash,
                    profile_id=profile_id,
                    profile_version=profile_version,
                    profile_ref_hash=profile_ref_hash,
                    runtime=runtime,
                )
            else:
                rc = require_controls(req, permit)
                if rc is not None:
                    decision = deny_decision(
                        reason=rc,
                        request_hash=req_hash,
                        profile_id=profile_id,
                        profile_version=profile_version,
                        profile_ref_hash=profile_ref_hash,
                        runtime=runtime,
                    )
                else:
                    rc2 = enforce_constraints(req, permit)
                    if rc2 is not None:
                        decision = deny_decision(
                            reason=rc2,
                            request_hash=req_hash,
                            profile_id=profile_id,
                            profile_version=profile_version,
                            profile_ref_hash=profile_ref_hash,
                            runtime=runtime,
                        )
                    else:
                        decision = allow_decision(
                            request_hash=req_hash,
                            profile_id=profile_id,
                            profile_version=profile_version,
                            profile_ref_hash=profile_ref_hash,
                            tool_name=req.tool.name,
                            tool_args=req.tool.args,
                            runtime=runtime,
                        )

            decided_at = utc_now_iso()
            record = _audit_record_from_denied(
                request_id=request_id,
                request_hash=req_hash,
                profile_id=profile_id,
                profile_version=profile_version,
                profile_ref_hash=profile_ref_hash,
                decision_type=decision.decision_type,
                reason_code=decision.reason_code.value,
                runtime=decision.runtime.model_dump(),
                received_at=received_at,
                decided_at=decided_at,
            )
            await anyio.to_thread.run_sync(append_audit_record, record)
            return decision.model_dump()



        except Exception:
            # Hard fail-closed fallback (still logs)
            req_hash = sha256_prefixed(raw)
            decision = deny_decision(
                reason=ReasonCode.INTERNAL_ERROR,
                request_hash=req_hash,
                profile_id=profile_id,
                profile_version=profile_version,
                profile_ref_hash=profile_ref_hash,
                runtime=runtime,
            )
            decided_at = utc_now_iso()
            record = _audit_record_from_denied(
                request_id=request_id,
                request_hash=req_hash,
                profile_id=profile_id,
                profile_version=profile_version,
                profile_ref_hash=profile_ref_hash,
                decision_type=decision.decision_type,
                reason_code=decision.reason_code.value,
                runtime=decision.runtime.model_dump(),
                received_at=received_at,
                decided_at=decided_at,
            )
            await anyio.to_thread.run_sync(append_audit_record, record)
            return decision.model_dump()

    return app


def _audit_record_from_denied(
    request_id: str,
    request_hash: str,
    profile_id: str,
    profile_version: str,
    profile_ref_hash: str,
    runtime: Dict[str, Any],
    received_at: str,
    decided_at: str,
    decision_type: str = None,
    reason_code: str = None,
    approved_call: Dict[str, Any] = None,
    decision: Dict[str, Any] = None,
    **_: Any,
) -> Dict[str, Any]:
    logged_at = utc_now_iso()

    runtime_version = (
        runtime.get("runtime_version")
        or runtime.get("version")
        or runtime.get("app_version")
        or runtime.get("runtime")
        or "0"
    )

    prov_id = provenance_id_from_inputs(
        request_hash=request_hash,
        profile_ref_hash=profile_ref_hash,
        runtime_version=runtime_version,
    )

    # Normalize decision fields (fail-closed defaults)
    if decision is not None:
        d = dict(decision)
        dt = d.get("decision_type") or decision_type or "DENY"
        rc = d.get("reason_code") or reason_code or "INTERNAL_ERROR"
        ac = d.get("approved_call", approved_call)
    else:
        dt = decision_type or "DENY"
        rc = reason_code or "INTERNAL_ERROR"
        ac = approved_call

    record = {
        "provenance_id": prov_id,
        "seq": 0,  # overwritten by audit append
        "request_id": request_id,
        "request_hash": request_hash,

        # ✅ keep legacy/top-level shape (tests expect this)
        "decision_type": dt,
        "reason_code": rc,
        "approved_call": ac,

        "profile_id": profile_id,
        "profile_version": profile_version,
        "profile_ref_hash": profile_ref_hash,
        "runtime": runtime,
        "timestamps": {
            "received_at": received_at,
            "decided_at": decided_at,
            "logged_at": logged_at,
        },
    }

    return record
