import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class EvalCase:
    name: str
    prompt: str
    checks: List[str]


class Evaluator:
    def __init__(self, cli_path: str = "python3 -m apps.agent.cli"):
        self.cli_path = cli_path

    def run_case(self, case: EvalCase) -> Dict[str, Any]:
        tmpdir = tempfile.mkdtemp(prefix="agent_eval_")
        try:
            # prepare empty project
            os.makedirs(os.path.join(tmpdir, "workspace"), exist_ok=True)
            cmd = f"{self.cli_path} run {json.dumps(case.prompt)} --repo-path {json.dumps(os.path.join(tmpdir, 'workspace'))} --max-steps 12 | cat"
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            passed = proc.returncode == 0
            check_results = []
            for check in case.checks:
                cr = subprocess.run(check, shell=True, cwd=tmpdir, capture_output=True, text=True)
                check_results.append({"check": check, "code": cr.returncode, "stdout": cr.stdout, "stderr": cr.stderr})
                if cr.returncode != 0:
                    passed = False
            return {"name": case.name, "passed": passed, "stdout": proc.stdout, "stderr": proc.stderr, "checks": check_results}
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


def default_cases() -> List[EvalCase]:
    return [
        EvalCase(
            name="todo_cli_min",
            prompt="Create a minimal Python CLI todo app using Typer saved under ./workspace/todo with add/list/done and tests.",
            checks=[
                "python3 -c \"import pathlib,sys; p=pathlib.Path('workspace/todo'); sys.exit(0 if p.exists() else 1)\"",
            ],
        ),
    ]


def run_all():
    ev = Evaluator()
    results = [ev.run_case(c) for c in default_cases()]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    run_all()


