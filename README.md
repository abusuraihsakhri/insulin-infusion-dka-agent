# Insulin Infusion DKA Agent

> **Domain:** Clinical Pharmacology & Precision Pharmacotherapy
> **Reference Guidelines & Standards:** CPIC Guidelines & FDA Table of Pharmacogenomic Biomarkers

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Insulin Infusion DKA Agent** is an advanced analytical and computational platform implementing DKA/HHS Hourly Regular Insulin & Potassium Interlock Sentinel. It evaluates clinical metrics through specialized worker agents, enforces zero-PHI outbound data protection, and maintains a cryptographically tamper-evident audit trail.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`GlucoseDropVelocityAgent`**: Specialized Sub-Agent 1 for insulin-infusion-dka-agent
- **`PotassiumThresholdInterlockAgent`**: Specialized Sub-Agent 2 for insulin-infusion-dka-agent
- **`DKAResolutionAuditorAgent`**: Specialized Sub-Agent 3 for insulin-infusion-dka-agent

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/insulin-infusion-dka-agent.git
cd insulin-infusion-dka-agent

# Install production dependencies
pip install -e .

# Install development dependencies (for testing)
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env to set your AUDIT_SECRET_KEY
```

---

## 💻 CLI Quickstart & Usage

### 1. Run Single Audit
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Query Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Process CSV
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier
- `--target`: Target entity or specimen identifier
- `--primary`: Primary metric measurement (float)
- `--secondary`: Secondary metric measurement (float)
- `--critical`: Flag for emergency escalation
- `--status`: Status descriptor (e.g., NOMINAL, DISCORDANT)

### Input Data Schema (CSV Batch)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Target entity identifier | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary measurement value | Required |
| `status_descriptor` | Status code or phenotype | Optional |
| `is_critical_flag` | Emergency escalation flag | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Input Validation:** All metric values validated as finite numbers (NaN/Inf rejected).
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t insulin-infusion-dka-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key insulin-infusion-dka-agent
```

Or using Docker Compose:

```bash
AUDIT_SECRET_KEY=your-secret-key docker-compose up
```

---

## 📁 Project Structure

```
insulin-infusion-dka-agent/
├── agents/                  # Core agent modules
│   ├── api.py              # FastAPI REST endpoints
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── models.py           # Pydantic data models
│   ├── supervisor.py       # Master orchestrator
│   ├── workers.py          # Specialized evaluation workers
│   ├── llm_factory.py      # LLM provider factory
│   ├── metrics.py          # Prometheus metrics
│   ├── learning.py         # Bayesian calibration engine
│   └── streamer.py         # WebSocket telemetry
├── tests/                  # Test suite
├── cli.py                  # Command-line interface
├── dka_guard.py            # DKAGuard coordinator & sub-agents
├── enrichment.py           # Enrichment feature engines
├── simulator.py            # High-throughput simulation
├── pyproject.toml          # Project configuration
├── Dockerfile              # Container build
└── docker-compose.yml      # Container orchestration
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
