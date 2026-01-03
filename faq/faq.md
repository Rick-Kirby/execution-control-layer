# Frequently Asked Questions

## Status

This FAQ is **non-normative**. It addresses common questions about the Execution Control Layer and does not define requirements, constraints, or implementation guidance.

---

## General Questions

### Is ECL a product, service, or component?

No. The canonical specification states:

> "The Execution Control Layer (ECL) is not a component, service, agent, or tool."

ECL is an architectural control boundary, not a software artifact. It describes where governance occurs in a system architecture, not what software implements it.

### Is ECL vendor-specific or model-specific?

No. ECL is vendor-agnostic and model-agnostic. It defines architectural invariants that apply regardless of which AI models, execution tools, or infrastructure platforms are in use.

### Does ECL replace existing enterprise systems?

No. The specification states:

> "ECL does not replace existing enterprise control systems."

ECL operates at the execution control boundary. It does not subsume or replace workflow orchestration, identity and access management, policy authoring platforms, or other enterprise governance systems.

### What does ECL actually do?

The specification states:

> "The Execution Control Layer governs how decisions are executed, not which decisions are made."

ECL provides deterministic governance at the moment intent transitions to action. It evaluates whether an execution request satisfies governance constraints and issues a binding gate decision.

---

## Scope and Boundaries

### Does ECL participate in reasoning or planning?

No. The specification explicitly states:

> "ECL does not participate in reasoning, policy creation, or action implementation."

ECL operates at the execution boundary. It does not generate intent, modify intent, or participate in upstream reasoning processes.

### Does ECL orchestrate workflows or manage task sequences?

No. ECL governs individual execution requests at the moment they are initiated. It does not coordinate tasks, manage state across multiple execution cycles, or schedule activities.

### Does ECL make AI decisions safer or more correct?

ECL governs whether decisions may proceed to execution. It does not make reasoning outputs safer, more accurate, or more aligned. Safety and correctness of reasoning are upstream concerns.

ECL enforces governance constraints on execution. If those constraints are correctly authored and appropriately scoped, ECL ensures they are applied deterministically. ECL does not determine whether constraints themselves are correct or sufficient.

---

## Determinism and Behaviour

### What does determinism mean in the ECL context?

Determinism means that governance evaluation produces the same gate decision given the same intent, referenced state, and control version. The specification states:

> "ECL provides deterministic governance at the transition boundary between intent and execution."

Determinism applies to control behaviour, not to the outputs of AI reasoning systems. Probabilistic models may produce different outputs across invocations, but ECL governance evaluation over those outputs is deterministic.

### Does determinism mean ECL always makes the same decision?

Determinism means identical inputs produce identical outputs. If the intent, referenced state, or control version changes, the gate decision may differ. Determinism ensures predictability and consistency under fixed conditions, not uniformity across all conditions.

### Can ECL adapt or learn from past decisions?

No. ECL applies governance evaluation based on the current intent, referenced state, and control version. It does not learn, adapt, or modify its behaviour based on past execution cycles.

Policy evolution occurs through authoring processes outside the ECL boundary. ECL applies policies as presented.

---

## Auditability and Compliance

### Does ECL guarantee compliance with regulations or standards?

No. The specification states:

> "Auditability supports investigation and verification. Audit records do not determine compliance outcomes."

ECL provides provenance records that enable verification of control behaviour. Interpretation of those records and determination of compliance with legal, regulatory, or organizational requirements occur outside the ECL boundary.

### Does ECL ensure ethical or responsible AI behaviour?

No. ECL enforces governance constraints as defined in policies. It does not assess whether those constraints are ethically appropriate or sufficient for responsible AI deployment.

Ethical alignment and responsibility are determined through policy authoring, organizational governance processes, and broader societal considerations. ECL enforces what is defined, not what should be defined.

### Can auditability alone prove conformance?

Auditability enables verification through inspection and testing. Provenance records provide evidence of control behaviour. Conformance assessment requires both sufficient provenance and behavioural verification under diverse conditions.

Interface observability and audit trails are necessary but not sufficient for conformance determination.

---

## Implementation and Conformance

### Can a system partially conform to ECL?

No. The specification states:

> "Partial conformance is non-conformance."

Conformance requires satisfaction of all architectural invariants. A system that satisfies some invariants but violates others is non-conformant.

### How is conformance verified?

Conformance is verified through inspection of interface properties, testing of behavioural invariants, and review of provenance records. Verification does not rely on vendor claims or certifications.

The Reference Architecture provides guidance on mapping invariants to observable interface properties to support third-party verification.

### Does ECL prescribe specific implementation approaches?

No. The specification states:

> "Contracts define constraints, not implementation techniques."

ECL defines what properties conformant systems must exhibit, not how those properties are achieved. Implementation choices are unconstrained provided architectural invariants hold.

---

## Relationship to Other Architectural Concerns

### How does ECL relate to identity and access management?

ECL operates at a higher conceptual level than IAM. IAM controls who may access resources. ECL governs whether specific execution requests may proceed given governance constraints.

IAM and ECL address different concerns and may coexist in the same architecture.

### How does ECL relate to observability and monitoring systems?

Observability systems consume provenance records emitted by ECL. They provide operational visibility, alerting, and analysis. ECL produces structured audit records. Observability systems interpret and act on those records.

### How does ECL relate to policy authoring and governance platforms?

Policy authoring occurs upstream of ECL. Governance platforms may provide tools for creating, versioning, and managing policies. ECL applies those policies at the execution boundary.

ECL consumes policies. It does not author or modify them.

---

## Common Misunderstandings

### Is the Reference Architecture a deployment guide?

No. Appendix A states:

> "Its purpose is strictly explanatory."

The Reference Architecture clarifies placement, boundaries, and realizability. It does not prescribe deployment patterns, infrastructure choices, or operational procedures.

### Does ECL introduce overhead or latency?

The specification does not define performance characteristics. Governance evaluation occurs at the execution boundary. Whether this introduces material latency depends on implementation choices, policy complexity, and system architecture.

Performance is an implementation concern, not an architectural invariant.

### Can ECL be bypassed in exceptional circumstances?

The specification states:

> "All governed execution paths must pass through ECL. Execution that bypasses ECL is ungoverned and falls outside the guarantees provided by this specification."

Bypassing ECL invalidates governance guarantees. Whether to permit ungoverned execution is an organizational decision. ECL does not define exception mechanisms.

### Does ECL require specific infrastructure or platforms?

No. ECL is infrastructure-agnostic. It defines architectural invariants that can be satisfied across diverse infrastructure environments, deployment models, and technology stacks.

---

This FAQ addresses common questions. For authoritative definitions and requirements, consult the canonical specification and normative supplements.
