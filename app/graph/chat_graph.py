from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.graph.nodes.check_search import check_search
from app.graph.nodes.decide_search_type import decide_search_type
from app.graph.nodes.classify_input import classify_input
from app.graph.nodes.condition_collector import collect_conditions
from app.graph.nodes.sql_search import sql_search
from app.graph.nodes.vector_search import vector_search

# 기본 condition 키를 모두 빈값으로 초기화
DEFAULT_CONDITION = {
    "gender": None,
    "age": None,
    "place": None,
    "work_days": None,
    "start_time": None,
    "end_time": None,
    "hourly_wage": None,
    "requirements": None,
    "category": None
}

class ChatState(BaseModel):
    user_id: Optional[str] = None
    text: str
    condition: Dict[str, Any] = DEFAULT_CONDITION.copy()
    search: bool = False

    is_job_related: Optional[bool] = None
    response: Optional[str] = None
    result: Optional[List[Dict[str, Any]]] = []

graph = StateGraph(ChatState)

graph.add_node("check_search", check_search)
graph.add_node("decide_search_type", decide_search_type)
graph.add_node("classify_input", classify_input)
graph.add_node("collect_conditions", collect_conditions)
graph.add_node("sql_search", sql_search)
graph.add_node("vector_search", vector_search)

graph.set_entry_point("check_search")

# 1-1) check_search > classify_input > collect_conditions
# 1-2) check_search > classify_input > END

# 2-1) check_search > decide_search_type > vector_search
# 2-2) check_search > decide_search_type > sql_search

graph.add_conditional_edges(
    "check_search",
    lambda s: "decide_search_type" if s.search else "classify_input",
    {"decide_search_type": "decide_search_type", "classify_input": "classify_input"},
)

graph.add_conditional_edges(
    "classify_input",
    lambda s: "collect_conditions" if s.is_job_related else END,
    {"collect_conditions": "collect_conditions", END: END},
)

graph.add_conditional_edges(
    "decide_search_type",
    lambda s: "vector_search" if s.condition.get("requirements") else "sql_search",
    {"vector_search": "vector_search", "sql_search": "sql_search"},
)

graph.add_edge("collect_conditions", END)
graph.add_edge("vector_search", END)
graph.add_edge("sql_search", END)

workflow = graph.compile()
