import subprocess, shlex
from typing import Dict, Callable


def run_cmd(cfg: Dict) -> Callable:
    timeout_sec = int(cfg.get("timeout_sec", 60))
    allowlist = set(cfg.get("allowlist", []))

    def _tool(command: str):
        cmd_parts = shlex.split(command)
        if not cmd_parts or cmd_parts[0] not in allowlist:
            return {"error": "command not allowed"}
        try:
            out = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_sec,
                check=False,
                text=True,
            )
            return {"code": out.returncode, "stdout": out.stdout, "stderr": out.stderr}
        except subprocess.TimeoutExpired:
            return {"error": "timeout"}

    return _tool

