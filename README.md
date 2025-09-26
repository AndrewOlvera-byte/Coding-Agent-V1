## Coding Agent MVP (LangGraph + LiteLLM)

### Setup

1. Copy `.env.example` to `.env` and fill keys
2. Install Python deps:

```bash
pip install -r requirements.txt
```

3. Start API:

```bash
uvicorn apps.agent.main:app --reload
```

4. Run CLI:

```bash
python -m apps.agent.cli run --goal "Initialize repo" --repo-path ./workspace
```

5. Run eval harness:

```bash
python -m apps.eval.harness
```

### Config
See `config/agent.yaml` for model, planner, tools, memory.


