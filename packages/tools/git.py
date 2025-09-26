import subprocess
from typing import Callable


def _run_git(args):
    proc = subprocess.run(["git"] + args, capture_output=True, text=True)
    return {"code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def git_status() -> Callable:
    return lambda: _run_git(["status", "--porcelain=v1"])


def git_diff() -> Callable:
    return lambda: _run_git(["diff"])


def git_commit() -> Callable:
    def _tool(message: str):
        _run_git(["add", "-A"])
        return _run_git(["commit", "-m", message])

    return _tool

