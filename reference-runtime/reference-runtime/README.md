
---

# Execution Control Layer (ECL) — Reference Runtime

This repository contains a **minimal, runnable reference runtime** for the **Execution Control Layer (ECL)** architectural specification.

Its purpose is to make the ECL standard **executable, testable, and falsifiable**.

This is **not** a framework, **not** a product, and **not** a policy system.

---

## What This Is

* A **single execution gate** implementing a deterministic, fail-closed control boundary between AI reasoning and real-world execution
* A **conformance target** for systems claiming ECL compatibility
* A **verification artifact** that proves ECL invariants are enforceable in code
* A **measurement surface** for observing execution-time behavior under load

The runtime exposes exactly **one execution surface**:
`POST /v1/execute`

> Non-bypassability is demonstrated **within the reference wiring**: all execution requests must pass through this gate.

---

## What This Is Not

* Not an agent framework
* Not a tool runtime (it never executes tools)
* Not a policy authoring system
* Not a governance platform
* Not an orchestration engine
* Not autonomous
* Not production software

This runtime **only decides** whether an execution request is allowed, denied, or escalated.
It does **not** perform the execution.

---

## Core Properties (Verified)

The following properties are enforced and verified by the test harness:

* **Deterministic decisions**
  Identical inputs produce identical decisions and provenance.

* **Fail-closed behavior**
  Any ambiguity, malformed input, missing profile, or internal error results in denial.

* **Non-bypassable execution gate**
  All decisions flow through a single, explicit control boundary.

* **Static, versioned execution profiles**
  Decisions are bound to immutable profile IDs and exact profile bytes via hash.

* **Explicit allowlist enforcement**
  Tools not explicitly permitted are denied.

* **Control requirements enforcement**
  Required controls (e.g. approval tokens) are enforced deterministically.

* **Constraint enforcement**
  Per-tool constraints are evaluated deterministically.

* **One-decision-per-request invariant**
  Every execution attempt produces exactly one decision and one audit record.

* **Immutable audit & provenance**
  Every decision emits an append-only, hash-chained audit record.

If a system cannot pass this harness, **it is not ECL-conformant**.

---

## Conformance Harness

### Run all tests

```powershell
python -m pytest -q
```

Latest verified result at time of publication:

* **11 tests passed**
* **0 failures**
* **1 non-fatal httpx deprecation warning**

The harness validates:

* determinism & replayability
* fail-closed semantics
* profile enforcement
* constraint enforcement
* audit hash-chain integrity
* provenance binding
* canonicalization invariance

---

## Runtime

### Start the server

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000
```

### Multiprocess (for load testing)

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
```

---

## Docker

This reference runtime can be built and executed as a Docker container to ensure
environment-independent reproducibility.

### Build the image

From the repository root:

```bash
docker build -t ecl-ref .
```

### Run the container

```bash
docker run --rm -p 8000:8000 ecl-ref
```

The execution gate will be available at:

```
POST http://127.0.0.1:8000/v1/execute
```

### Multiprocess execution

The container supports multi-process execution using the ASGI server’s worker model:

```bash
docker run --rm -p 8000:8000 ecl-ref \
  uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

This configuration is used for load and scaling observations only.
It does **not** alter ECL semantics.

### Audit persistence in Docker

Audit persistence is controlled via the `AUDIT_LOG_PATH` environment variable.

Example (benchmarking only):

```bash
docker run --rm -p 8000:8000 \
  -e AUDIT_LOG_PATH="/dev/null" \
  ecl-ref
```

Example (per-process sharded audit logs):

```bash
docker run --rm -p 8000:8000 \
  -e AUDIT_LOG_PATH="/logs/ecl_audit_{pid}.log" \
  -v $(pwd)/logs:/logs \
  ecl-ref
```

Audit sharding preserves all ECL invariants while avoiding cross-process file contention.
Global ordering across shards is explicitly out of scope for this reference runtime.

---

## Load Testing

A minimal async load generator is included.

### Baseline load test

```powershell
$env:PYTHONPATH="."
python scripts/load.py --requests 20000 --concurrency 200
```

The load script reports:

* total OK / FAIL
* wall time
* throughput (requests/sec)
* latency percentiles (p50 / p95 / p99)

---

## Audit Persistence & Scaling Observations

Audit persistence materially affects throughput under high concurrency.

### Audit enabled (single shared file)

```powershell
$env:PYTHONPATH="."
python scripts/load.py --requests 20000 --concurrency 200
```

Observed (Windows, local, workers=4):

* ~**154 req/s**
* non-zero failures under saturation
* p99 latency ~5s

---

### Audit disabled (benchmark only)

> **Note:** Disabling audit persistence is for benchmarking only.

**Windows**

```powershell
$env:AUDIT_LOG_PATH="NUL"
$env:PYTHONPATH="."
python scripts/load.py --requests 20000 --concurrency 200
Remove-Item Env:\AUDIT_LOG_PATH -ErrorAction SilentlyContinue
```

**Linux**

```bash
AUDIT_LOG_PATH="/dev/null" python scripts/load.py --requests 20000 --concurrency 200
```

Observed:

* ~**188 req/s**
* ~22% throughput increase vs single-file audit

---

### Sharded audit streams (semantics preserved)

The runtime supports `{pid}` expansion in `AUDIT_LOG_PATH` to avoid cross-process file contention.

```powershell
New-Item -ItemType Directory -Force -Path .\logs | Out-Null
$env:AUDIT_LOG_PATH="logs\ecl_audit_{pid}.log"
$env:PYTHONPATH="."
python scripts/load.py --requests 20000 --concurrency 200
Remove-Item Env:\AUDIT_LOG_PATH -ErrorAction SilentlyContinue
```

Observed (Windows, local, workers=4):

* **~279 req/s**
* **0 failures**
* p99 latency ~5.3s

This configuration:

* preserves all ECL invariants
* preserves deterministic audit hash chains **per stream**
* removes cross-process audit file contention

Global ordering across shards is **explicitly out of scope** for this reference runtime.

---

## What These Benchmarks Do (and Do Not) Prove

### They demonstrate:

* determinism under load
* fail-closed behavior under stress
* audit persistence as a measurable execution-time factor
* semantics-preserving scalability via horizontal replication

### They do **not** claim:

* linear scaling
* absolute enterprise throughput numbers
* multi-node or distributed performance
* global total ordering of audit logs

All measurements are **local, Windows-based**, and topology-dependent.

---

## Out of Scope

This repository intentionally does **not** include:

* policy authoring tools
* governance workflows
* execution engines
* distributed consensus
* global audit aggregation
* learning or adaptation
* orchestration logic

Those concerns belong **outside** the ECL boundary.

---

## Purpose

This runtime exists to answer one question:

> *“Can a deterministic, fail-closed execution-time control boundary be enforced and verified in code?”*

The answer, demonstrated here, is **yes**.

---
