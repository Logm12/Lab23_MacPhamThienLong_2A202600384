# Project Directory Report

## Overview
**Project Name**: `day08-langgraph-agent-lab`
**Description**: Starter skeleton for LangGraph agentic orchestration lab.
**Environment**: Python >= 3.11 with LangGraph ecosystem dependencies.

---

## Directory Structure

```text
.
├── .env.example             # Example environment variable configuration
├── Dockerfile               # Container definition
├── docker-compose.yml       # Multi-container orchestration setup
├── Makefile                 # Standard make commands for shortcut actions
├── README.md                # Project main documentation
├── pyproject.toml           # Build system requirements and configurations
├── configs/
│   └── lab.yaml             # Application and experimentation configuration 
├── data/
│   └── sample/
│       └── scenarios.jsonl  # Test data / scenarios for routing evaluation
├── docs/
│   ├── LAB_GUIDE.md         # Detailed guidance for completing the lab tasks
│   ├── METRICS.md           # Definitions of performance evaluation metrics
│   └── RUBRIC.md            # Grading benchmarks for evaluating agents
├── outputs/
│   └── .gitkeep             # Output directory for artifacts/runs (excluded from git)
├── reports/
│   └── lab_report_template.md # Template for finalizing evaluation summaries
├── src/
│   └── langgraph_agent_lab/ # Core Source Package
│       ├── __init__.py
│       ├── cli.py           # CLI entry point via Typer (`agent-lab`)
│       ├── graph.py         # LangGraph structure and logic builders
│       ├── metrics.py       # Logic for accuracy and latency metrics
│       ├── nodes.py         # Functional nodes for the workflow
│       ├── persistence.py   # Checkpointers and database handling
│       ├── report.py        # Generation logic for the final markdown report
│       ├── routing.py       # Conditional routing and decisions
│       ├── scenarios.py     # Scenario definitions loading and parsing
│       └── state.py         # LangGraph TypedDict State definitions
└── tests/                   # Comprehensive Test Suite
    ├── test_graph_smoke.py  # Basic Graph execution flow verification
    ├── test_metrics.py      # Unit tests verifying math/computation reliability
    ├── test_routing.py      # Edge case routing conditional tests
    └── test_state.py        # State reducer and validation checks
```

---

## System Artifact Analysis

- **Root Manifests**: Driven by `pyproject.toml`, mapping scripts directly to `langgraph_agent_lab.cli:app` via command `agent-lab`.
- **Core Logic (`src/`)**: Modular structure that strictly enforces separate concerns between the LangGraph lifecycle (`graph.py`, `nodes.py`, `routing.py`, `state.py`) and auxiliary workflows (`metrics.py`, `report.py`).
- **Documentation Set**: Comprehensive onboarding docs split across guiding principles (`LAB_GUIDE.md`) and formal evaluation criterion (`RUBRIC.md`).

---
*Generated automatically on: 2026-05-11*
