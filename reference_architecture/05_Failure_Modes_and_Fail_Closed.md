# Failure Modes and Fail-Closed Behaviour

## Status

This document is **non-normative**. It explains failure modes and fail-closed behaviour in the context of ECL and does not define requirements, constraints, or implementation guidance.

## Failure as Deterministic Architectural Outcome

The canonical specification states:

> "The Execution Control Layer fails structurally and deterministically. Failure is an expected and controlled outcome of governance evaluation."

Failure is not an exceptional condition or implementation defect. It is a first-class architectural outcome that occurs when governance evaluation denies execution or when structural conditions prevent evaluation from completing.

The specification clarifies:

> "Failure is an expected and enforceable outcome of execution-time governance."

Failure behaviour is subject to the same architectural invariants as successful execution. It must be deterministic, auditable, and verifiable.

## Fail-Closed Execution

Fail-closed behaviour means that when governance evaluation cannot proceed or when evaluation denies execution, the system suppresses execution rather than allowing it to proceed.

The specification states:

> "Clean execution suppression prevents intent from executing without corrupting control state."

Fail-closed ensures that uncertain or denied governance outcomes do not result in uncontrolled execution. If the ECL boundary cannot issue a valid gate decision, execution does not occur.

This architectural posture prioritizes governance guarantees over availability. A system that permits execution when governance evaluation fails is fail-open and violates ECL architectural invariants.

## Failure Modes

The specification defines the following failure modes:

> "ECL defines the following failure modes: Governance Denial, Deterministic Policy Propagation, Clean Execution Suppression, and Auditable Silent Failure."

### Governance Denial

Governance denial occurs when evaluation determines that the intent violates an applicable policy constraint. The gate decision is HALT. Execution is suppressed.

Governance denial is an expected outcome of policy enforcement. It reflects the normal operation of the ECL boundary when intent does not satisfy governance constraints.

### Deterministic Policy Propagation

Deterministic policy propagation occurs when misconfigured or incomplete policies produce consistent denial outcomes.

The specification states:

> "Misconfigured policies produce consistent, auditable control outcomes."

Even if policies are incorrectly authored, their application must be deterministic. Given the same intent and control version, a misconfigured policy produces the same governance outcome across executions.

The specification further clarifies:

> "ECL does not self-correct policy errors."

ECL applies policies as presented. It does not detect or remediate policy misconfigurations. Detection of incorrect policy outcomes occurs through audit and review, not through internal ECL logic.

### Clean Execution Suppression

Clean execution suppression occurs when structural conditions prevent governance evaluation from completing. Examples include malformed intent, unavailable referenced state, or inability to resolve control version.

Execution is suppressed without partial execution or state corruption. Control state remains consistent.

The specification states:

> "Clean execution suppression prevents intent from executing without corrupting control state."

Suppression is observable through provenance records. An audit trail captures the suppression event, the reason, and the intent that was denied.

### Auditable Silent Failure

Auditable silent failure occurs when governance evaluation completes and issues a gate decision of ABSTAIN or HALT, suppressing execution without generating user-visible errors.

From the perspective of the execution mechanism, no action occurs. From the perspective of the audit system, a complete provenance record is emitted.

Silent failure is not a defect. It reflects the architectural principle that governance operates at the execution boundary, not at the user interface or orchestration layer. Interpretation of denied execution and determination of user-facing responses occur outside the ECL boundary.

## Finality of Failure Outcomes

The specification states:

> "Within a single execution cycle, failure outcomes are final."

Once a failure outcome occurs, it cannot be reconsidered or overridden within the same execution cycle. Retry, appeal, or re-evaluation require a new execution cycle with potentially different inputs or control versions.

This finality ensures consistency and predictability. Failure outcomes are binding in the same way that successful execution is binding.

## Determinism in Failure

The specification states:

> "Non-deterministic failure behaviour violates architectural invariants."

Failure must be deterministic under identical conditions. Given the same intent, referenced state, and control version, failure occurs consistently.

Non-deterministic failure, where identical inputs produce different outcomes across executions, indicates non-conformance. Verification of determinism applies to both successful execution and failure modes.

## Relationship Between Denial, Suppression, and Auditability

Governance denial results in execution suppression. Suppression is observable through provenance records. Provenance enables verification that suppression occurred deterministically and in accordance with policy constraints.

Auditability of failure is as important as auditability of successful execution. Provenance records must capture:

* The intent that was denied
* The gate decision issued (ABSTAIN or HALT)
* The reason for denial, if applicable
* The control version in effect
* The outcome (suppression of execution)

These records enable post hoc review and verification of failure behaviour.

## Properties of Reviewable Failure Behaviour

The specification states:

> "Failure outcomes are consistent, enforceable, and provable."

For failure behaviour to be reviewable and verifiable, it must exhibit the following properties:

* **Consistency**: Identical inputs produce identical failure outcomes across executions.
* **Enforceability**: Failure outcomes suppress execution completely and deterministically.
* **Provability**: Provenance records provide sufficient evidence to reconstruct and verify failure behaviour.

These properties enable third-party verification without requiring access to internal implementation logic.

## Failure Does Not Trigger Corrective Logic

ECL does not respond to failure by attempting self-correction, policy override, or alternative evaluation paths.

The specification states:

> "ECL does not self-correct policy errors."

Failure is reported through provenance emission. Remediation, policy correction, or alternative approaches occur outside the ECL boundary through organizational processes, policy authoring workflows, or user intervention.

ECL enforces governance as defined. It does not modify governance in response to failure outcomes.

## Detection of Non-Conformance Through Failure Behaviour

Failure behaviour enables detection of non-conformance in the same way that successful execution does.

Non-conformance may be detected when:

* Identical inputs produce different failure outcomes across executions
* Execution proceeds despite governance denial
* Failure corrupts control state or produces partial execution
* Provenance records of failure are incomplete or inconsistent

Verification of failure behaviour is part of conformance assessment. A system that handles successful execution deterministically but fails non-deterministically is non-conformant.

## Separation of Failure Semantics from Recovery Mechanisms

ECL defines what happens at the execution control boundary when governance evaluation denies execution or when structural conditions prevent evaluation from completing.

ECL does not define:

* How systems respond to denied execution upstream or downstream of the ECL boundary
* Retry logic, compensation, or rollback mechanisms
* User-facing error messages or notifications
* Operational alerting or monitoring responses

These concerns are distinct from execution control failure semantics. Organizations determine how to respond to governance denial and execution suppression based on their operational, user experience, and business requirements.
