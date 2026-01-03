# Reference Architecture Diagrams

## Status

These diagrams are **non-normative** and **illustrative only**. They support visual understanding of ECL architectural placement and control flow. They do not define requirements, constraints, or behaviour.

---

## Diagram 1: Architectural Placement of ECL

This diagram illustrates the positioning of the Execution Control Layer as an intermediary boundary between reasoning systems and execution mechanisms.

```mermaid
graph TB
    A[AI Reasoning Systems]
    B[Execution Control Layer Boundary]
    C[Execution Mechanisms]
    D[Execution Suppressed]
    
    A -->|Intent| B
    B -->|Gate Decision: EXECUTE| C
    B -->|Gate Decision: Execution Suppressed| D
    
    style B fill:#f9f9f9,stroke:#333,stroke-width:3px
```

---

## Diagram 2: Intent to Action Boundary

This diagram illustrates the control boundary where intent becomes action, mediated by governance evaluation.

```mermaid
graph LR
    A[Referenced State Presented] --> B[Intent Generated]
    B --> C[Intent Validated]
    C --> D[Governance Evaluated]
    D --> E[Gate Decision Issued]
    E -->|EXECUTE| F[Action Performed]
    E -->|Execution Suppressed| G[Action Suppressed]

```

---

## Diagram 3: Ordered Execution State Sequence

This diagram illustrates the ordered state sequence within a single execution cycle as governed by ECL.

```mermaid
graph TD
    A[Referenced State Presented] --> B[Intent Generated]
    B --> C[Intent Validated]
    C --> D[Governance Evaluated]
    D --> E[Gate Decision Issued]
    E --> F{Gate Decision}
    F -->|EXECUTE| G[Execution Occurs]
    F -->|ABSTAIN or HALT| H[Execution Suppressed]
    G --> I[State Transition Applied]
    H --> J[Execution Suppressed]
    I --> K[Audit Record Emitted]
    J --> K
    
    style D fill:#f9f9f9,stroke:#333,stroke-width:2px
    style E fill:#f9f9f9,stroke:#333,stroke-width:2px
```

---

All diagrams reflect architectural concepts defined in the canonical specification and do not prescribe implementation approaches.
