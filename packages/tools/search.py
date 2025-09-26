import subprocess, json
from typing import Callable


def rg_search() -> Callable:
    def _tool(pattern: str, path: str = ".", glob: str = ""):
        cmd = ["rg", "--json", pattern, path]
        if glob:
            cmd = ["rg", "--json", "--glob", glob, pattern, path]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        results = []
        for line in proc.stdout.splitlines():
            try:
                results.append(json.loads(line))
            except Exception:
                pass
        return {"code": proc.returncode, "results": results, "stderr": proc.stderr}

    return _tool


