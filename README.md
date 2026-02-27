# AIRMAN AI Dispatch Agent

A constraint-aware flight dispatch and dynamic reallocation system built using **FastAPI, PostgreSQL, Redis, Docker, and LangGraph orchestration**.

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

# 🏗 System Architecture

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

## Core Modules

- `ingestion.py` → Seeds instructors, aircraft, and operational data  
- `roster_generator.py` → Generates baseline weekly schedule  
- `reallocation_engine.py` → Applies disruption handling logic  
- `compliance_engine.py` → Enforces safety & operational rules  
- `capacity_manager.py` → Prevents resource conflicts  
- `evaluation_harness.py` → Stress testing & churn metrics  
- `langgraph_orchestrator.py` → Workflow orchestration layer  

---

# 🔁 LangGraph Workflow

LangGraph orchestrates the disruption handling pipeline:

1. Event ingestion  
2. Disruption classification  
3. Reallocation execution  
4. Compliance validation  
5. Explanation generation  

This enables modular, auditable, and structured state transitions.

---

# 🚀 Quick Start

## 1️⃣ Clone Repository

---

## Core Modules

- `ingestion.py` → Seeds instructors, aircraft, and operational data  
- `roster_generator.py` → Generates baseline weekly schedule  
- `reallocation_engine.py` → Applies disruption handling logic  
- `compliance_engine.py` → Enforces safety & operational rules  
- `capacity_manager.py` → Prevents resource conflicts  
- `evaluation_harness.py` → Stress testing & churn metrics  
- `langgraph_orchestrator.py` → Workflow orchestration layer  

---

# 🔁 LangGraph Workflow

LangGraph orchestrates the disruption handling pipeline:

1. Event ingestion  
2. Disruption classification  
3. Reallocation execution  
4. Compliance validation  
5. Explanation generation  

This enables modular, auditable, and structured state transitions.

---

# 🚀 Quick Start

## 1️⃣ Clone Repository
git clone <your-repo-url>
cd airman-roster-engine


## 2️⃣ Start System
docker-compose up --build


## 3️⃣ Open Swagger UI
http://localhost:8000/docs


---

# 📡 API Endpoints

## 1️⃣ Run Data Ingestion
POST /ingest/run

Seeds instructors, aircraft, and training data.

---

## 2️⃣ Generate Baseline Roster
GET/roster/generate

Creates deterministic weekly training schedule.

---

## 3️⃣ Reallocate (LangGraph Orchestrated)
POST /roster/reallocate-graph


Triggers disruption workflow and dynamic reallocation.

---

## 4️⃣ Stress Test Evaluation

Triggers disruption workflow and dynamic reallocation.

---

## 4️⃣ Stress Test Evaluation
POST /eval/stress-test


Runs multiple disruption scenarios and reports:

- Total events  
- Average churn  
- Maximum churn  
- Compliance violations  

---

# 📊 Evaluation Metrics

The system measures:

- **Churn rate** (schedule changes per event)  
- **Diff count**  
- **Compliance violations**  
- **Session success rate**  

Stress scenarios executed with:

- Zero safety violations  
- Controlled reallocation churn  
- Deterministic behavior  

---

# ⚖️ Design Tradeoffs

| Decision | Reason |
|----------|--------|
| Deterministic scheduling | Ensures auditability & safety |
| Constraint-based engine | Safety-first design |
| LangGraph orchestration | Structured workflow control |
| No ML optimization | Predictability over probabilistic behavior |
| Modular engines | Clear separation of concerns |

---

# 🛠 Tech Stack

- FastAPI  
- PostgreSQL  
- Redis  
- SQLAlchemy  
- LangGraph  
- Docker & Docker Compose  
- GitHub Actions CI  
- Flake8 Linting  

---

# 🔬 Evaluation & Stress Testing

The evaluation harness simulates:

- Weather degradation  
- Aircraft failures  
- Instructor reassignment  
- Recovery scenarios  

Metrics demonstrate:

- Controlled churn  
- Zero compliance violations  
- Operational validity under disruption  

---

# 🔮 Future Improvements

- Multi-week optimization  
- Instructor fatigue modeling  
- Aircraft predictive maintenance  
- Probabilistic weather modeling  
- ML-based optimization under constraints  

---

# 📂 Repository Structure

airman-roster-engine/
│
├── README.md
├── PLAN.md
├── CUTS.md
├── POSTMORTEM.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .github/
└── app/