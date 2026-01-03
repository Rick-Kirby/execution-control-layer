# Control Boundary and Flow

## Status

This document is **non-normative**. It explains the control boundary and execution flow governed by ECL and does not define requirements, constraints, or behaviour.

## The Intent to Action Boundary

The canonical specification states:

> "The Execution Control Layer operates at the boundary where intent becomes action."

This boundary is the defining control point of the architecture. Intent represents a request to perform an execution-capable action. The ECL boundary intercepts that intent, applies governance evaluation, and enforces a binding control decision before any action occurs.

As stated in the specification:

> "ECL intercepts intent, applies governance evaluation, and enforces binding control decisions prior to execution."

## Intent as Immutable Input

Intent enters the ECL boundary as immutable input. ECL does not modify, reinterpret, or negotiate intent. It evaluates whether the intent, as presented, may proceed to execution.

The specification clarifies:

> "The Execution Control Layer governs how decisions are executed, not which decisions are made."

Intent formation occurs upstream of the ECL boundary. ECL does not participate in reasoning, planning, or orchestration. It governs the transition from formed intent to executed action.

Appendix A states:

> "ECL enforces governance at execution time, not during intent formation."

## Governance Evaluation

Governance evaluation is a mandatory step within the ECL boundary. It is not advisory, optional, or deferrable.

The specification states:

> "Governance decisions must be binding, not advisory."

Evaluation produces a gate decision that determines whether intent may proceed to execution. This decision is final within a single execution cycle and must not be reconsidered.

The specification states:

> "Within a single execution cycle, the gate decision issued is final and must not be reconsidered."

## Gate Decisions

The specification defines three possible gate decisions:

> "ECL defines three possible gate decisions: EXECUTE, ABSTAIN, and HALT."

### EXECUTE

The EXECUTE decision permits the intent to proceed to execution. The execution mechanism receives the intent and performs the requested action.

### ABSTAIN

The ABSTAIN decision declines to issue a determination. The intent does not proceed to execution. ABSTAIN is a gate decision that suppresses execution without permitting the action to proceed.

### HALT

The HALT decision actively suppresses execution. The intent does not proceed. HALT represents an explicit prohibition, typically issued when governance evaluation determines that the intent violates an applicable policy constraint.

### Semantic Distinction

ABSTAIN and HALT differ in intent and interpretation. ABSTAIN reflects absence of governance applicability. HALT reflects presence of governance prohibition. Both suppress execution, but the reason and audit implications differ.

## Execution State Machine

The canonical specification defines an ordered state machine governing a single execution cycle:

> "Within a single execution cycle, states must be traversed in the following sequence:
>
> 1. Referenced State Presented
> 2. Intent Generated
> 3. Intent Validated
> 4. Governance Evaluated
> 5. Gate Decision Issued
> 6. Execution or Suppression
> 7. State Transition Applied
> 8. Audit Record Emitted"

The specification further mandates:

> "No step in this sequence may be skipped. No step may be reordered."

### Conceptual Explanation of States

**Referenced State Presented**: The system state referenced by the intent is made available to the ECL boundary. This state provides context for governance evaluation.

**Intent Generated**: The intent to perform an action is formed and presented to the ECL boundary. Intent includes the action, parameters, and execution context.

**Intent Validated**: The intent is structurally validated. Malformed or incomplete intent cannot proceed.

**Governance Evaluated**: Applicable policies are evaluated against the intent and referenced state. This evaluation is deterministic and produces a gate decision.

**Gate Decision Issued**: One of the three gate decisions (EXECUTE, ABSTAIN, HALT) is issued. This decision is final and binding within the execution cycle.

**Execution or Suppression**: If the gate decision is EXECUTE, the intent proceeds to the execution mechanism. If the gate decision is ABSTAIN or HALT, execution is suppressed.

**State Transition Applied**: If execution occurred, any resulting state change is applied to the system. If execution was suppressed, no state change occurs.

**Audit Record Emitted**: A complete audit record is emitted. The record includes the intent, gate decision, execution outcome, and any relevant context.

## Determinism and Finality

The execution state machine is deterministic. Given the same intent and referenced state, governance evaluation produces the same gate decision. Within a single execution cycle, no step may be revisited, and no decision may be overturned.

This determinism is foundational to the architecture. It ensures predictability, auditability, and consistency.

## What ECL Does Not Do

ECL does not participate in reasoning, orchestration, or execution itself. It does not generate intent, modify intent, implement actions, or manage system state. It governs the boundary between intent and action, applying deterministic evaluation and enforcing binding control decisions.
