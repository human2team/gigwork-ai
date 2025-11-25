# app/graph/nodes/post_intent_router.py
from app.graph.state import ChatState


def post_intent_router(state: ChatState) -> ChatState:
    """
    상태만 유지. 실제 분기는 graph.py에서 처리.
    """
    return state
