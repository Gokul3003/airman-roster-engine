# CUTS.md

## Scope Reductions (Intentional)

To ensure deterministic and auditable behavior within evaluation constraints, the following were intentionally excluded:

### 1. Machine Learning Optimization
- No probabilistic optimization
- No reinforcement learning
- No predictive modeling

Reason:
Safety and explainability prioritized over heuristic optimization.

---

### 2. Multi-Week Planning
- Only single-week scheduling implemented

Reason:
Keeps system evaluation deterministic and bounded.

---

### 3. Instructor Fatigue Modeling
- No cumulative fatigue tracking

Reason:
Out of scope for current evaluation.

---

### 4. Advanced Weather Forecasting
- Uses structured weather input instead of predictive modeling

Reason:
Ensures repeatable evaluation behavior.

---

## Summary

The system prioritizes:
- Safety
- Determinism
- Explainability
- Auditability
