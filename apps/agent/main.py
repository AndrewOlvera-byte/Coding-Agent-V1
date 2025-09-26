import os, json, yaml
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import litellm
from typing import Dict, Any

# simple memory + tool registry placeholders
from packages.memory.vector import VectorMemory
from packages.tools.registry import ToolRegistry
from packages.orchestration.graph import build_graph, run_graph

load_dotenv()

CFG_PATH = os.environ.get("AGENT_CONFIG", "config/agent.yaml")
with open(CFG_PATH, "r") as f:
    CFG = yaml.safe_load(f)

# Configure LiteLLM dynamically from YAML + .env
litellm.drop_params = True
MODEL_NAME = (
    f"{CFG['model']['provider']}/{CFG['model']['name']}"
    if "/" not in CFG["model"]["name"]
    else CFG["model"]["name"]
)

# instantiate tools and memory
tools = ToolRegistry.from_config(CFG["tools"])
memory = VectorMemory.from_config(CFG["memory"])

graph = build_graph(
    model_name=MODEL_NAME,
    planner_cfg=CFG["planner"],
    tools=tools,
    memory=memory,
)

app = FastAPI()


class RunRequest(BaseModel):
    goal: str
    repo_path: str = "./workspace"
    max_steps: int = 30


@app.post("/run")
async def run(req: RunRequest):
    state: Dict[str, Any] = {
        "goal": req.goal,
        "repo_path": req.repo_path,
        "steps": [],
        "working_memory": [],
    }
    result = await run_graph(graph, state, max_steps=req.max_steps)
    return result


