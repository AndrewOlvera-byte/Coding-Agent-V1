from typing import Dict
from .fs import fs_read, fs_write
from .shell import run_cmd
from .git import git_status, git_diff, git_commit
from .search import rg_search
from .web import web_search


class ToolRegistry:
    def __init__(self, tools):
        self.tools = tools

    @classmethod
    def from_config(cls, cfg: Dict):
        enabled = set(cfg.get("enabled", []))
        tools = {}
        fs_cfg = dict(cfg.get("fs", {}))
        # Dynamically extend allowlist with AGENT_REPO_ROOT if provided
        try:
            import os
            repo_root = os.environ.get("AGENT_REPO_ROOT", "").strip()
            if repo_root:
                roots = list(fs_cfg.get("root_allowlist", ["./workspace"]))
                if repo_root not in roots:
                    roots.append(repo_root)
                fs_cfg["root_allowlist"] = roots
        except Exception:
            pass
        if "fs_read" in enabled:
            tools["fs_read"] = fs_read(fs_cfg)
        if "fs_write" in enabled:
            tools["fs_write"] = fs_write(fs_cfg)
        if "terminal" in enabled:
            tools["terminal"] = run_cmd(cfg.get("terminal", {}))
        if "git" in enabled:
            tools["git_status"] = git_status()
            tools["git_diff"] = git_diff()
            tools["git_commit"] = git_commit()
        if "rg_search" in enabled:
            tools["rg_search"] = rg_search()
        if "web_search" in enabled:
            tools["web_search"] = web_search()
        return cls(tools)

