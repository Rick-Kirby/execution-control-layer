# Appendix A — Architectural Placement (Non-Normative)

**Status:** Non-normative explanatory appendix  
**Relationship to Canon:** This appendix does not modify, extend, or supersede the canonical *Execution Control Layer (ECL) — Architectural Specification v1.0*.  
In the event of any inconsistency, the canonical specification takes precedence.

---

## Purpose

This appendix exists solely to clarify **where** the Execution Control Layer (ECL) resides within a concrete system architecture.

It is intentionally non-operational and non-prescriptive.  
No implementation guidance, algorithms, workflows, or examples are provided.

---

## Architectural Placement

The Execution Control Layer (ECL) is not a component, service, agent, or tool.

It is a **control boundary** that exists at the moment probabilistic reasoning transitions into real-world execution.

In a concrete system, ECL semantics may be realised through a variety of architectural forms, including but not limited to:

- a control-plane enforcement boundary  
- an execution gate  
- a policy-bound runtime mediator  
- a transactionally enforced execution wrapper  

The defining characteristic is **not** the technology, location, or deployment model.

The defining characteristic is that **no execution-capable action may occur unless mediated by the ECL boundary**, and that this mediation is deterministic, auditable, and fail-closed.

---

## Relationship to Reasoning and Orchestration

The ECL does not participate in reasoning, planning, or orchestration.

- Reasoning systems determine *what should happen*  
- Orchestration systems determine *how work is coordinated*  
- The Execution Control Layer determines *whether execution is permitted*

ECL enforces governance at execution time, not during intent formation.

---

## Implicit Presence in Existing Systems

Many AI-driven systems already contain **implicit execution boundaries** (e.g. API gateways, workflow triggers, permission checks).

However, without an explicit Execution Control Layer, these boundaries:

- are bypassable  
- are non-deterministic under probabilistic reasoning  
- do not enforce invariant-level governance  
- cannot be reliably audited as execution controls  

ECL formalises this boundary as a first-class architectural concern.

---

## Non-Goals (Clarification)

This appendix does not:

- define how ECL should be implemented  
- recommend specific architectures or patterns  
- provide reference designs or workflows  
- establish compliance criteria or certification processes  

Its purpose is strictly explanatory.

---

## Normative Reference

All mandatory architectural invariants, control semantics, and determinism requirements for the Execution Control Layer (ECL) are defined exclusively in: [execution-control-layer-architectural-specification-v1.0.md](execution-control-layer-architectural-specification-v1.0.md)


This appendix exists only to support correct interpretation of the canonical specification.


