# PLAN

## Objective

Design and implement a constraint-aware flight dispatch system capable of dynamic reallocation under operational disruptions.

---

## Phase 1 – Core Scheduling Engine

- JSON data ingestion into PostgreSQL
- Weekly roster generation
- Instructor allocation logic
- Aircraft allocation logic
- Weather minima evaluation
- Basic compliance validation

---

## Phase 2 – Dynamic Reallocation

- Weather disruption handling
- Aircraft failure handling
- Instructor unavailability handling
- Simulator substitution logic
- Capacity manager
- Cost-aware churn minimization

---

## Phase 3 – Orchestration & Evaluation

- LangGraph orchestration layer
- Structured state transitions
- Stress testing harness
- Compliance reporting
- Version tracking

---

## Success Criteria

- Zero compliance violations
- Controlled churn under disruption
- Deterministic and auditable scheduling
- Fully Dockerized reproducible system