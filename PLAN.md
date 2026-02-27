# PLAN.md

## Project Objective

Design and implement a constraint-aware AI dispatch and reallocation system capable of:

- Generating deterministic weekly training rosters
- Handling operational disruptions
- Maintaining zero compliance violations
- Minimizing schedule churn

---

## Phase 1 – Core Scheduling Engine

- Implement data ingestion module
- Build deterministic roster generator
- Enforce instructor, aircraft, and student constraints
- Validate operational compliance

---

## Phase 2 – Reallocation Engine

- Handle weather disruptions
- Handle aircraft failures
- Handle instructor unavailability
- Minimize churn during rescheduling
- Preserve compliance guarantees

---

## Phase 3 – Orchestration Layer

- Integrate LangGraph for workflow orchestration
- Create structured disruption pipeline
- Add explanation generation

---

## Phase 4 – Evaluation Harness

- Simulate stress scenarios
- Measure churn
- Track compliance violations
- Generate evaluation summary

---

## Phase 5 – Productionization

- Dockerize API + DB + Redis
- Add CI pipeline
- Add documentation
- Prepare demo video
