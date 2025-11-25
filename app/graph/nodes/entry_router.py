# app/graph/nodes/.py
from app.graph.state import ChatState


def entry_router(state: ChatState) -> ChatState:
    """
    단순 입구 역할. 분기 조건은 graph.py에서 처리.
    """
    return state
