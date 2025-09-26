import os, requests
from typing import Callable


def web_search() -> Callable:
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

    def _tool(query: str, k: int = 5):
        resp = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": TAVILY_API_KEY, "query": query, "max_results": k},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    return _tool

