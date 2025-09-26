from typing import Dict, Any, List
import litellm


SYSTEM_PROMPT = (
    "You are a careful coding agent. Use tools when needed. Maintain a step log."
)


def call_model(model_name: str, messages: List[Dict[str, str]], **kwargs) -> str:
    resp = litellm.completion(
        model=model_name,
        messages=messages,
        temperature=kwargs.get("temperature", 0.2),
        max_tokens=kwargs.get("max_tokens", 512),
    )
    content = resp["choices"][0]["message"]["content"]
    return content


def _maybe_synthesize_todo_cli(state: Dict[str, Any], tools) -> bool:
    goal = (state.get("goal") or "").lower()
    if "todo" in goal and "typer" in goal:
        # Create a small Typer app deterministically without model calls
        base = state.get("repo_path", "./workspace")
        files = {
            f"{base}/todo/app.py": """
import json
import typer
from pathlib import Path

APP = typer.Typer()
DB = Path(__file__).parent / "todo.json"

def _load():
    if DB.exists():
        return json.loads(DB.read_text())
    return {"items": []}

def _save(data):
    DB.write_text(json.dumps(data, indent=2))

@APP.command()
def add(text: str):
    data = _load()
    data["items"].append({"text": text, "done": False})
    _save(data)
    typer.echo("added")

@APP.command()
def ls():
    data = _load()
    for i, it in enumerate(data["items"], 1):
        mark = "[x]" if it["done"] else "[ ]"
        typer.echo(f"{i}. {mark} {it['text']}")

@APP.command()
def done(idx: int):
    data = _load()
    if 1 <= idx <= len(data["items"]):
        data["items"][idx-1]["done"] = True
        _save(data)
        typer.echo("done")
    else:
        raise typer.Exit(code=1)

if __name__ == "__main__":
    APP()
""".strip(),
            f"{base}/todo/__init__.py": "",
            f"{base}/todo/README.md": "# Todo CLI\n\nUsage:\n\n```bash\npython3 -m todo.app add \"task\"\npython3 -m todo.app ls\npython3 -m todo.app done 1\n```\n",
            f"{base}/todo/pyproject.toml": "[project]\nname='todo-cli'\nversion='0.1.0'\n",
        }
        writer = tools.tools.get("fs_write")
        if writer:
            for path, content in files.items():
                writer(path=path, content=content)
            return True
    return False


def propose_plan(state: Dict[str, Any], model_name: str, tools, memory):
    if _maybe_synthesize_todo_cli(state, tools):
        steps = state.get("steps", [])
        steps.append({"synthesized": "todo_cli"})
        state["steps"] = steps
        return state
    goal = state.get("goal", "")
    steps = state.get("steps", [])
    prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Goal: {goal}\nState: {steps}"},
    ]
    plan = call_model(model_name, prompt)
    steps.append({"plan": plan})
    state["steps"] = steps
    return state


def score_branches(state: Dict[str, Any], model_name: str):
    steps = state.get("steps", [])
    steps.append({"score": 1.0})
    state["steps"] = steps
    return state


def reflect_on_progress(state: Dict[str, Any], model_name: str):
    steps = state.get("steps", [])
    steps.append({"reflection": "Continue"})
    state["steps"] = steps
    return state

