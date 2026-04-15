# OracleForge Data Analytics Agent

Production-oriented multi-database analytics agent for the TRP1 Oracle Forge challenge.

## Team Roster and Roles
- Drivers: Nurye, Kemerya
- Intelligence Officers: Amare, Ephrata
- Signal Corps: Yohanis, Addisu

## Live Agent Access (Shared Server)
- Public live endpoint: `https://oracle-forge-sandbox.yohannesdereje1221.workers.dev/`
- Shared-server health endpoint: `http://YOUR_SHARED_SERVER_HOST:8080/health`
- Query endpoint (CLI over SSH on shared host):
  - `python3 -m agent.data_agent.cli "What was the maximum adjusted closing price in 2020 for The RealReal, Inc.?" --db-hints '["sqlite","duckdb"]'`

Replace `YOUR_SHARED_SERVER_HOST` with your team's shared-server host/IP before final submission (public endpoint above is already live).

## Architecture Diagram
```mermaid
flowchart TD
    U[Facilitator / User Question] --> CLI[agent/data_agent/cli.py]
    CLI --> OFA[oracle_forge_agent.py]
    OFA --> C[OracleForgeConductor]

    C --> CL[Context Layering\n6-layer assembly]
    C --> KB[Knowledge Base Retrieval\nkb/architecture + kb/domain + kb/evaluation + kb/corrections]
    C --> MEM[MemoryManager\nindex + topics + sessions]
    C --> REG[Tool Registry + Policy]

    REG --> MCP[MCP Toolbox\nPostgreSQL / MongoDB / SQLite]
    REG --> DDB[DuckDB Bridge]

    C --> EV[Event Ledger\n.oracle_forge_memory/events.jsonl]
    C --> OUT[AgentResult\nanswer + confidence + trace_id + tool_calls]
```

## Architecture (Component Map)
- Public facade: `agent/data_agent/oracle_forge_agent.py`
- Runtime orchestration: `agent/runtime/conductor.py`
- Unified DB client: `agent/data_agent/mcp_toolbox_client.py`
- DuckDB bridge client: `agent/data_agent/duckdb_bridge_client.py`
- Context layering + KB retrieval: `agent/data_agent/context_layering.py`, `agent/data_agent/knowledge_base.py`
- Memory + event ledger: `agent/runtime/memory.py`, `agent/runtime/events.py`
- Optional sandbox execution path: `agent/data_agent/sandbox_client.py`, `sandbox/sandbox_server.py`

## Clean-Machine Setup (Facilitator Runbook)
1. Clone the repository.
```bash
git clone <repo-url>
cd data-analytics-agent
```
2. Create and activate Python environment.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3. Copy environment template.
```bash
cp .env.example .env
```
4. Start local infra stack.
```bash
docker compose -f docker-compose.yml up -d
./scripts/healthcheck_stack.sh
```
5. Run one agent query end-to-end.
```bash
python3 -m agent.data_agent.cli \
  "What was the maximum adjusted closing price in 2020 for The RealReal, Inc.?" \
  --db-hints '["sqlite","duckdb"]'
```
6. Run tests.
```bash
python3 -m unittest discover -s tests -v
```
7. Run evaluation harness baseline.
```bash
python3 eval/run_trials.py --trials 2 --output results/smoke.json
python3 eval/score_results.py --results results/smoke.json
```

## Non-Obvious Dependency and Environment Assumptions
- Docker Compose v2 is required (`docker compose`, not legacy `docker-compose`).
- `external/DataAgentBench` must exist locally because eval scripts read benchmark query folders directly.
- If `external/DataAgentBench` is missing, clone it:
```bash
git clone https://github.com/ucbepic/DataAgentBench.git external/DataAgentBench
```

## DAB-Compatible Function Interface
`agent/data_agent/dab_interface.py` provides:

```python
run_agent(question: str, available_databases: list[dict], schema_info: dict) -> dict
```

## Repository Deliverables Map
- Agent code: `agent/`
- Knowledge base: `kb/`
- Evaluation harness: `eval/`
- Adversarial probes: `probes/probes.md`
- Planning/governance docs: `planning/`
- Signal/communication artifacts: `signal/`
- Benchmark outputs + score log: `results/`
- Shared utility modules: `utils/`
