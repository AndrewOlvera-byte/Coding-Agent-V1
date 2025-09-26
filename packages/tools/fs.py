import os
from typing import Callable, Dict


def _is_allowed(path: str, root_allowlist):
    abs_path = os.path.abspath(path)
    for root in root_allowlist:
        abs_root = os.path.abspath(root)
        if abs_path.startswith(abs_root + os.sep) or abs_path == abs_root:
            return True
    return False


def fs_read(cfg: Dict) -> Callable:
    roots = cfg.get("root_allowlist", ["./workspace"])

    def _tool(path: str, max_bytes: int = 200_000):
        if not _is_allowed(path, roots):
            return {"error": "path not allowed"}
        try:
            with open(path, "rb") as f:
                data = f.read(max_bytes)
            try:
                return {"path": path, "content": data.decode("utf-8")}
            except UnicodeDecodeError:
                return {"path": path, "content_b64": data.hex()}
        except Exception as e:
            return {"error": str(e)}

    return _tool


def fs_write(cfg: Dict) -> Callable:
    roots = cfg.get("root_allowlist", ["./workspace"])
    max_kb = int(cfg.get("max_write_kb", 256))

    def _tool(path: str, content: str):
        if not _is_allowed(path, roots):
            return {"error": "path not allowed"}
        data = content.encode("utf-8")
        if len(data) > max_kb * 1024:
            return {"error": "write too large"}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return {"ok": True, "path": path, "bytes": len(data)}

    return _tool

