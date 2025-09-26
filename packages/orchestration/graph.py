from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .policies import propose_plan, reflect_on_progress, score_branches


def build_graph(model_name: str, planner_cfg: Dict, tools, memory):
    sg = StateGraph(dict)
    sg.add_node("plan", lambda s: propose_plan(s, model_name, tools, memory))
    sg.set_entry_point("plan")
    if planner_cfg.get("strategy") in ("tot", "beam", "mcts"):
        sg.add_node("branch_score", lambda s: score_branches(s, model_name))
        sg.add_edge("plan", "branch_score")
        sg.add_node("reflect", lambda s: reflect_on_progress(s, model_name))
        sg.add_edge("branch_score", "reflect")
        sg.add_edge("reflect", "plan")
    else:
        sg.add_edge("plan", END)

    checkpointer = MemorySaver()
    return sg.compile(checkpointer=checkpointer)


async def run_graph(graph, state: Dict[str, Any], max_steps: int):
    it = graph.astream(state, config={"recursion_limit": max_steps})
    final = None
    async for s in it:
        final = s
    return final or state

