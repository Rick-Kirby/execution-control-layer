from __future__ import annotations

import re
from typing import Any, Dict, Optional

from .models import ExecutionProfile, ExecutionRequest, ReasonCode, ToolPermit


def find_tool_permit(profile: ExecutionProfile, tool_name: str) -> Optional[ToolPermit]:
    for p in profile.allowed_tools:
        if p.name == tool_name:
            return p
    return None


def require_controls(req: ExecutionRequest, permit: ToolPermit) -> Optional[ReasonCode]:
    if permit.required_controls.approval_token:
        token = (req.controls.approval_token if req.controls else None)
        if not token:
            return ReasonCode.CONTROL_REQUIRED
        # Deterministic reference rule (no external checks)
        if token != "APPROVED":
            return ReasonCode.CONTROL_REQUIRED
    return None


def _get_arg_value(args: Any, path: str) -> Any:
    """
    Minimal path support for demo rules:
      - "$.key" for dict lookup
    Anything else -> error (fail closed).
    """
    if not path.startswith("$."):
        raise ValueError("unsupported path")
    key = path[2:]
    if not isinstance(args, dict):
        raise ValueError("args not object")
    return args.get(key, None)


def enforce_constraints(req: ExecutionRequest, permit: ToolPermit) -> Optional[ReasonCode]:
    if not permit.constraints or not permit.constraints.arg_rules:
        return None

    args = req.tool.args

    try:
        for rule in permit.constraints.arg_rules:
            v = _get_arg_value(args, rule.path)

            # Missing value fails closed for constrained fields
            if v is None:
                return ReasonCode.CONSTRAINT_VIOLATION

            if rule.type == "string":
                if not isinstance(v, str):
                    return ReasonCode.CONSTRAINT_VIOLATION
                if rule.max_len is not None and len(v) > rule.max_len:
                    return ReasonCode.CONSTRAINT_VIOLATION
                if rule.enum is not None and v not in rule.enum:
                    return ReasonCode.CONSTRAINT_VIOLATION
                if rule.pattern is not None and re.match(rule.pattern, v) is None:
                    return ReasonCode.CONSTRAINT_VIOLATION

            elif rule.type == "number":
                if not isinstance(v, (int, float)):
                    return ReasonCode.CONSTRAINT_VIOLATION
                if rule.min is not None and float(v) < rule.min:
                    return ReasonCode.CONSTRAINT_VIOLATION
                if rule.max is not None and float(v) > rule.max:
                    return ReasonCode.CONSTRAINT_VIOLATION

            elif rule.type == "bool":
                if not isinstance(v, bool):
                    return ReasonCode.CONSTRAINT_VIOLATION

            else:
                # Unknown rule type -> fail closed
                return ReasonCode.CONSTRAINT_EVAL_ERROR

        return None
    except Exception:
        return ReasonCode.CONSTRAINT_EVAL_ERROR
