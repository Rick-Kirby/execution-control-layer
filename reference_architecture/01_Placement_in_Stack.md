# Placement in Stack

## Status

This document is **non-normative**. It clarifies architectural placement only and does not define requirements, constraints, or behaviour.

## The Execution Control Layer as Architectural Boundary

The Execution Control Layer is not a component, service, agent, or tool. It is a control boundary that exists at the moment probabilistic reasoning transitions into real-world execution.

The defining characteristic is that no execution-capable action may occur unless mediated by the ECL boundary, and that this mediation is deterministic, auditable, and fail-closed.

## Position Within System Architecture

The canonical specification states:

> "The Execution Control Layer is positioned as an intermediary layer between AI reasoning systems and execution mechanisms."

ECL operates at the boundary where intent becomes action. It sits between:

* **Above**: AI reasoning systems, planning systems, orchestration layers, and policy authoring environments
* **Below**: Execution mechanisms, tools, APIs, and systems that perform real-world actions


The specification further clarifies:

> "ECL does not replace AI reasoning systems or execution mechanisms. It provides deterministic governance over the transition from decision to action."

## What ECL Does Not Subsume

ECL does not participate in reasoning, planning, or orchestration. It enforces governance at execution time, not during intent formation.

The canonical specification explicitly states:

> "ECL does not participate in reasoning, policy creation, or action implementation. It applies governance evaluation at the moment of execution initiation."

ECL is architecturally distinct from:

* **AI models and agents**: ECL does not generate decisions, plans, or responses. It governs the execution of decisions made by reasoning systems.
* **Workflow orchestration systems**: ECL does not coordinate tasks, manage state, or schedule activities. It evaluates individual execution requests at the moment of initiation.
* **Policy authoring systems**: ECL does not create, edit, or version policies. It applies policies that have been authored elsewhere.
* **Execution systems and tools**: ECL does not perform actions. It governs whether actions may proceed.
* **Infrastructure and access control layers**: ECL operates at a higher conceptual level, governing the transition from intent to action rather than managing authentication, authorization, or resource access.

## Governance Scope

The specification mandates:

> "All governed execution paths must pass through ECL. Execution that bypasses ECL is ungoverned and falls outside the guarantees provided by this specification."

Any execution path that circumvents the ECL boundary invalidates the governance guarantees of the architecture. The boundary must be complete for the architecture to hold.

## Conceptual, Not Technological

Placement of the Execution Control Layer is conceptual and architectural. It describes a logical position within the control flow of a system, not a specific technological implementation, deployment topology, or physical location.

The boundary exists wherever the system transitions from probabilistic reasoning to deterministic execution, independent of code structure, infrastructure topology, or organizational process.
