from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict, model_validator


# ----------------------------
# Common config: strict + no surprises
# ----------------------------
STRICT = ConfigDict(extra="forbid", frozen=True)


# ----------------------------
# Reason codes (machine-verifiable)
# ----------------------------
class ReasonCode(str, Enum):
    OK = "OK"

    REQUEST_PARSE_ERROR = "REQUEST_PARSE_ERROR"
    REQUEST_SCHEMA_INVALID = "REQUEST_SCHEMA_INVALID"
    CTX_HASH_MISMATCH = "CTX_HASH_MISMATCH"

    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"
    PROFILE_PARSE_ERROR = "PROFILE_PARSE_ERROR"
    INVALID_PROFILE_DEFAULT = "INVALID_PROFILE_DEFAULT"

    TOOL_NOT_ALLOWED = "TOOL_NOT_ALLOWED"
    CONTROL_REQUIRED = "CONTROL_REQUIRED"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"
    CONSTRAINT_EVAL_ERROR = "CONSTRAINT_EVAL_ERROR"

    AUDIT_WRITE_FAILED = "AUDIT_WRITE_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# ----------------------------
# Execution Request
# ----------------------------
class Actor(BaseModel):
    model_config = STRICT

    principal_id: str = Field(min_length=1)
    principal_type: str = Field(min_length=1)
    attributes: Dict[str, str] = Field(default_factory=dict)


class ToolCall(BaseModel):
    model_config = STRICT

    name: str = Field(min_length=1)
    args: Any  # Opaque to ECL (but must be JSON-serializable for hashing)


class ProfileRef(BaseModel):
    model_config = STRICT

    id: str = Field(min_length=1)
    version: str = Field(min_length=1)


class Context(BaseModel):
    model_config = STRICT

    snapshot: Any  # Hashable JSON (we’ll canonicalize + hash it)
    snapshot_hash: str = Field(min_length=1)  # e.g. "sha256:<hex>"


class Controls(BaseModel):
    model_config = STRICT

    approval_token: Optional[str] = None
    nonce: Optional[str] = None


class ExecutionRequest(BaseModel):
    model_config = STRICT

    request_id: str = Field(min_length=1)
    actor: Actor
    tool: ToolCall
    profile: ProfileRef
    context: Context
    controls: Optional[Controls] = None

    # Logged only; NOT used in decision logic
    submitted_at: Optional[str] = None


# ----------------------------
# Execution Profile (static input)
# ----------------------------
class RequiredControls(BaseModel):
    model_config = STRICT

    approval_token: bool = False


class ArgRule(BaseModel):
    model_config = STRICT

    path: str = Field(min_length=1)      # e.g. "$.to"
    type: str = Field(min_length=1)      # "string", "number", "bool"
    pattern: Optional[str] = None        # regex
    max_len: Optional[int] = None
    enum: Optional[List[str]] = None
    min: Optional[float] = None
    max: Optional[float] = None


class Constraints(BaseModel):
    model_config = STRICT

    arg_rules: List[ArgRule] = Field(default_factory=list)


class ToolPermit(BaseModel):
    model_config = STRICT

    name: str = Field(min_length=1)
    required_controls: RequiredControls = Field(default_factory=RequiredControls)
    constraints: Optional[Constraints] = None


class ExecutionProfile(BaseModel):
    model_config = STRICT

    profile_id: str = Field(min_length=1)
    profile_version: str = Field(min_length=1)
    allowed_tools: List[ToolPermit] = Field(default_factory=list)

    # MUST be "DENY" (we fail-closed if profile says otherwise)
    default: str = "DENY"

    @model_validator(mode="after")
    def _default_must_be_deny(self) -> "ExecutionProfile":
        if self.default != "DENY":
            raise ValueError("profile.default must be DENY")
        return self


# ----------------------------
# Decision (output of gate)
# ----------------------------
class DecisionType(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"  # blocks execution


class RuntimeMeta(BaseModel):
    model_config = STRICT

    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    build: str = Field(min_length=1)  # git sha or build id


class DecisionProfileInfo(BaseModel):
    model_config = STRICT

    id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    profile_ref_hash: str = Field(min_length=1)  # sha256 of canonical profile bytes


class ApprovedCall(BaseModel):
    model_config = STRICT

    tool_name: str = Field(min_length=1)
    tool_args: Any


class ExecutionDecision(BaseModel):
    model_config = STRICT

    decision_type: DecisionType
    reason_code: ReasonCode

    request_hash: str = Field(min_length=1)
    provenance_id: str = Field(min_length=1)

    profile: DecisionProfileInfo
    runtime: RuntimeMeta

    # Present ONLY if decision_type == ALLOW
    approved_call: Optional[ApprovedCall] = None

    @model_validator(mode="after")
    def _allow_requires_approved_call(self) -> "ExecutionDecision":
        if self.decision_type == DecisionType.ALLOW and self.approved_call is None:
            raise ValueError("ALLOW requires approved_call")
        if self.decision_type != DecisionType.ALLOW and self.approved_call is not None:
            raise ValueError("approved_call must be absent unless ALLOW")
        return self


# ----------------------------
# Audit record (append-only)
# ----------------------------
class AuditTimestamps(BaseModel):
    model_config = STRICT

    received_at: str
    decided_at: str
    logged_at: str


class AuditIntegrity(BaseModel):
    model_config = STRICT

    prev_hash: str = Field(min_length=1)
    record_hash: str = Field(min_length=1)


class AuditRecord(BaseModel):
    model_config = STRICT

    provenance_id: str = Field(min_length=1)
    seq: int = Field(ge=0)

    request_id: str = Field(min_length=1)
    request_hash: str = Field(min_length=1)

    profile_id: str = Field(min_length=1)
    profile_version: str = Field(min_length=1)
    profile_ref_hash: str = Field(min_length=1)

    decision_type: DecisionType
    reason_code: ReasonCode

    runtime: RuntimeMeta
    timestamps: AuditTimestamps
    integrity: AuditIntegrity

