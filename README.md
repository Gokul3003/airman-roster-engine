# AIRMAN AI Dispatch Agent

A constraint-aware flight dispatch and dynamic reallocation system built using FastAPI, PostgreSQL, Redis, Docker, and LangGraph orchestration.

This system generates weekly training rosters and dynamically reallocates sessions in response to operational disruptions such as:

- Weather degradation
- Aircraft unavailability
- Instructor reassignment
- Operational capacity conflicts

The system guarantees:
- Deterministic scheduling
- Zero compliance violations
- Controlled churn during disruptions
- Audit-friendly traceability
- Workflow orchestration via LangGraph

---

# System Architecture

Client (Swagger / REST API)
        ↓
FastAPI Application
        ↓
LangGraph Orchestrator
        ↓
Reallocation Engine
        ↓
Compliance Engine
        ↓
Capacity Manager
        ↓
PostgreSQL (state) + Redis (optional cache)

---

# Core Modules

- ingestion.py → Seeds instructors, aircraft, and operational data
- roster_generator.py → Generates baseline weekly schedule
- reallocation_engine.py → Applies disruption handling logic
- compliance_engine.py → Enforces safety & operational rules
- capacity_manager.py → Prevents resource conflicts
- evaluation_harness.py → Stress testing & churn metrics
- langgraph_orchestrator.py → Workflow orchestration layer

---

# LangGraph Workflow

1. Event ingestion
2. Disruption classification
3. Reallocation execution
4. Compliance validation
5. Explanation generation

---

# Quick Start

1. Clone repository:
   git clone <your-repo-url>
   cd airman-roster-engine

2. Start system:
   docker-compose up --build

3. Open Swagger UI:
   http://localhost:8000/docs

---

# API Endpoints

POST /ingest/run
GET /roster/generate
POST /roster/reallocate-graph
POST /eval/stress-test

---

# Evaluation Metrics

- Churn rate
- Diff count
- Compliance violations
- Session success rate

---

# Tech Stack

- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- LangGraph
- Docker
- GitHub Actions CI

---

# Future Improvements

- Multi-week optimization
- Instructor fatigue modeling
- Aircraft predictive maintenance
- ML-based optimization under constraints

---

Author:
Gokula Kannan Jayakumar
