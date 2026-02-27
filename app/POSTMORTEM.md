# POSTMORTEM

## What Worked Well

- Modular engine-based architecture
- Clear separation between scheduling and orchestration
- Deterministic reallocation logic
- LangGraph integration for workflow control
- Stress testing validation

---

## Challenges Faced

- Handling datetime conversions between dict and Pydantic models
- Managing state transitions inside LangGraph
- Docker rebuild cycles during dependency changes
- Ensuring simulator capacity constraints remained consistent

---

## Lessons Learned

- Defensive programming prevents cascading failures
- Deterministic scheduling improves auditability
- Clear state models simplify orchestration
- Structured stress testing reveals edge-case instability

---

## Future Improvements

- Real-world weather API integration
- Global optimization solver
- Dashboard visualization
- Real-time operational monitoring