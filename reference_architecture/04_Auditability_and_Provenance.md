# Auditability and Provenance

## Status

This document is **non-normative**. It explains auditability and provenance in the context of ECL and does not define requirements, constraints, or implementation guidance.

## Auditability as Architectural Property

Auditability is an architectural property of the Execution Control Layer, not an operational feature or compliance mechanism. The canonical specification states:

> "The Execution Control Layer must produce structured provenance records that enable reconstruction and verification of control behaviour."

Auditability means that control behaviour can be observed, reconstructed, and verified through examination of provenance records. It provides evidence of what occurred at the ECL boundary without requiring access to internal implementation logic.

The specification clarifies:

> "Auditability supports investigation and verification. Audit records do not determine compliance outcomes."

Auditability enables verification but does not itself constitute compliance, correctness, or ethical alignment. It provides evidence for review, not judgement.

## Role of Provenance

Provenance records serve as the primary mechanism for auditability. They capture sufficient information to reconstruct control flow, verify determinism, and support post hoc investigation.

The specification states:

> "Audit records must capture intent content and structure, governance decisions issued, execution outcomes observed, and version identifiers."

Provenance enables:

* **Reconstruction of control flow**: Given a provenance record, it is possible to understand what intent was presented, what gate decision was issued, and what execution outcome occurred.
* **Verification of determinism**: Given multiple executions with identical inputs and versions, provenance records allow verification that gate decisions were identical.
* **Post hoc review and investigation**: Provenance provides evidence for understanding control behaviour after the fact, supporting investigation of unexpected outcomes or non-conformance.

## Properties of Provenance

The specification defines properties that provenance records must exhibit:

> "Audit records must be tamper-evident, replay-oriented, structured, and ordered."

### Tamper-Evident

Provenance records must be resistant to undetected modification. Any alteration to a provenance record after emission should be detectable through inspection or verification.

### Replay-Oriented

Provenance records must contain sufficient information to replay governance evaluation. Given a provenance record, it should be possible to reconstruct the inputs to governance evaluation and verify that the recorded gate decision is consistent with deterministic behaviour.

The specification states:

> "Replay enables verification of control determinism."

Replay does not mean re-execution of actions. It means re-evaluation of governance decisions given the same inputs and control version to verify consistency.

### Structured

Provenance records must conform to a defined structure. Unstructured or ambiguous records cannot support reliable reconstruction or verification.

### Ordered

Provenance records must preserve temporal ordering of execution cycles. Order is necessary to reconstruct sequences of control decisions and state transitions.

## Non-Influential Provenance

The specification states:

> "Provenance emission must be write-only and non-influential."

Provenance records are produced as output of the execution cycle. They do not participate in governance evaluation or influence gate decisions. Control flow proceeds independently of provenance capture.

This separation ensures that provenance provides evidence of behaviour without altering that behaviour. Provenance systems observe but do not interfere.

## Relationship Between Auditability, Replay, and Determinism

Auditability depends on determinism. Without deterministic control behaviour, provenance records cannot support verification because identical inputs might produce different outcomes.

Replay is the mechanism by which determinism is verified. Given a provenance record, replay reconstructs the governance evaluation using the recorded inputs and control version. If the replayed gate decision matches the recorded gate decision, determinism is confirmed for that execution cycle.

Provenance enables replay. Replay verifies determinism. Determinism enables auditability.

## What Auditability Does Not Provide

Auditability provides evidence of control behaviour. It does not provide:

* **Compliance determination**: Provenance records show what occurred but do not determine whether behaviour complied with legal, regulatory, or organizational requirements.
* **Ethical judgement**: Provenance records are factual. They do not assess whether control decisions were ethically appropriate.
* **Policy correctness**: Provenance shows that policies were applied but does not evaluate whether policies themselves were correct, complete, or desirable.

Auditability supports review and investigation by providing evidence. Interpretation of that evidence and determination of compliance, correctness, or appropriateness occur outside the ECL boundary.

## Detection of Non-Conformance

Auditability enables detection of non-conformance through inspection of provenance records and replay of governance evaluation.

Non-conformance may be detected when:

* Identical inputs and control versions produce different gate decisions across executions
* Provenance records are incomplete, malformed, or missing required information
* Replay of governance evaluation produces gate decisions inconsistent with recorded decisions
* Provenance records indicate that execution bypassed the ECL boundary

Detection of non-conformance depends on sufficient provenance capture and access to replay mechanisms.

## Separation of Concerns

The specification states:

> "ECL defines audit record structure and emission requirements but does not define storage, retention, access, or disclosure mechanisms."

Auditability is concerned with the production and structure of provenance records, not with their subsequent storage, retention, or use. These concerns are distinct:

* **Control behaviour**: The ECL boundary governs execution and produces provenance.
* **Audit systems**: Storage, retention, and access mechanisms for provenance records.
* **Organizational or legal processes**: Review, investigation, compliance determination, and remediation activities that consume provenance records.

ECL defines what provenance must contain and how it must be emitted. Organizations determine how provenance is stored, who may access it, and how it is used for review or compliance purposes.

## Third-Party Verification

Provenance records must be sufficient for third-party verification without requiring access to internal implementation logic or proprietary systems.

Third-party verification means that an independent reviewer, given provenance records and control versions, can:

* Reconstruct control flow for a given execution cycle
* Replay governance evaluation to verify determinism
* Detect non-conformance through inspection and testing

This capability depends on provenance records containing sufficient information and being structured for replay without privileged access to implementation internals.
