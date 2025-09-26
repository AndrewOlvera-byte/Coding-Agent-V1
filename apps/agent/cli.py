import asyncio
import json
import os
import yaml
import typer
from rich.console import Console
from dotenv import load_dotenv

from packages.orchestration.graph import build_graph, run_graph
from packages.tools.registry import ToolRegistry
from packages.memory.vector import VectorMemory

app = typer.Typer(add_completion=False, no_args_is_help=False)
console = Console()


@app.command()
def run(goal: str, repo_path: str = "./workspace", config: str = "config/agent.yaml", max_steps: int = 30):
    load_dotenv()
    with open(config, "r") as f:
        cfg = yaml.safe_load(f)
    # Extend FS allowlist at runtime for this repo
    os.environ["AGENT_REPO_ROOT"] = os.path.abspath(repo_path)
    model_name = (
        f"{cfg['model']['provider']}/{cfg['model']['name']}"
        if "/" not in cfg["model"]["name"]
        else cfg["model"]["name"]
    )
    tools = ToolRegistry.from_config(cfg["tools"])
    memory = VectorMemory.from_config(cfg["memory"])
    graph = build_graph(model_name, cfg["planner"], tools, memory)

    state = {"goal": goal, "repo_path": repo_path, "steps": [], "working_memory": []}

    async def _run():
        result = await run_graph(graph, state, max_steps=max_steps)
        console.print_json(data=result)

    asyncio.run(_run())


if __name__ == "__main__":
    app()


