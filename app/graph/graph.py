# app/graph/graph.py
from langgraph.graph import StateGraph, END
from app.graph.state import ChatState
from app.graph.nodes import (
    entry_router,
    intent_classifier_normal,
    intent_classifier_clarification,
    clarification_handler,
    post_intent_router,
    condition_add_handler,
    condition_modify_handler,
    postprocess_router,
    search_handler,
)

graph = StateGraph(ChatState)

# 노드 등록
graph.add_node("entry_router", entry_router)
graph.add_node("intent_classifier_normal", intent_classifier_normal)
graph.add_node("intent_classifier_clarification", intent_classifier_clarification)
graph.add_node("clarification_handler", clarification_handler)
graph.add_node("post_intent_router", post_intent_router)
graph.add_node("condition_add_handler", condition_add_handler)
graph.add_node("condition_modify_handler", condition_modify_handler)
graph.add_node("postprocess_router", postprocess_router)
graph.add_node("search_handler", search_handler)

# Entry
graph.set_entry_point("entry_router")

# Entry → intent 분기
graph.add_conditional_edges(
    "entry_router",
    lambda s: "intent_classifier_normal" if s.mode == "normal" else "intent_classifier_clarification",
    {
        "intent_classifier_normal": "intent_classifier_normal",
        "intent_classifier_clarification": "intent_classifier_clarification",
    },
)

# Normal classifier → post_intent_router
graph.add_edge("intent_classifier_normal", "post_intent_router")

# Clarification classifier 분기
graph.add_conditional_edges(
    "intent_classifier_clarification",
    lambda s: "clarification_handler" if s.intent_is_answer_to_question else "post_intent_router",
    {
        "clarification_handler": "clarification_handler",
        "post_intent_router": "post_intent_router",
    },
)

# Clarification handler → post_intent_router
graph.add_edge("clarification_handler", "post_intent_router")

# post_intent_router 분기
graph.add_conditional_edges(
    "post_intent_router",
    lambda s: (
        END if not s.intent_in_condition_related
        else "condition_add_handler" if s.intent_has_condition_text
        else "condition_modify_handler" if s.intent_has_modify_request
        else "postprocess_router"
    ),
    {
        "condition_add_handler": "condition_add_handler",
        "condition_modify_handler": "condition_modify_handler",
        "postprocess_router": "postprocess_router",
        END: END,
    },
)

# Handlers → postprocess_router
graph.add_edge("condition_add_handler", "postprocess_router")
graph.add_edge("condition_modify_handler", "postprocess_router")

# postprocess_router → search or END
graph.add_conditional_edges(
    "postprocess_router",
    lambda s: "search_handler" if s.intent_want_search and not s.error else END,
    {
        "search_handler": "search_handler",
        END: END,
    },
)

# search_handler → END
graph.add_edge("search_handler", END)

workflow = graph.compile()
