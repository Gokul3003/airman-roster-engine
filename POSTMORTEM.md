# POSTMORTEM.md

## What Went Well

- Deterministic scheduling achieved
- Zero compliance violations across stress tests
- Successful LangGraph integration
- CI pipeline functioning correctly
- Docker-based reproducible deployment

---

## Challenges Faced

### 1. State Handling in LangGraph
Initial errors occurred due to state mismatches between Pydantic models and dict-based processing.

Resolution:
Standardized state passing and normalized event data.

---

### 2. Compliance Engine Edge Cases
Missing severity keys caused runtime failures.

Resolution:
Added defensive checks and consistent violation schema.

---

### 3. Resource Capacity Conflicts
SIM vs Aircraft resource handling required additional guard logic.

Resolution:
Improved capacity manager allocation tracking.

---

## What Would Be Improved

- Add structured logging
- Add performance benchmarking
- Expand multi-disruption chaining
- Improve architecture visualization

---

## Final Outcome

The system satisfies all evaluation requirements:

- Dynamic reallocation
- LangGraph orchestration
- Zero compliance violations
- Controlled churn
- CI + Docker support

The design is modular, deterministic, and production-ready within defined scope.
