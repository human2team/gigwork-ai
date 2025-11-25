# app/graph/nodes/clarification_handler.py
from app.graph.state import ChatState, PendingTask


def clarification_handler(state: ChatState) -> ChatState:
    """
    intent_is_answer_to_question == True인 경우,
    pending_tasks에 맞게 state.conditions를 수정하거나 채운다.
    LLM 없이 직접 처리 (사전에 pending_task에 정보가 있음).
    """

    tasks = list(state.pending_tasks)
    for task in tasks:
        condition_type = task.condition_type

        if task.operation_type == "replace":
            state.conditions[condition_type] = task.condition_value

        elif task.operation_type == "add":
            if isinstance(state.conditions.get(condition_type), list):
                state.conditions[condition_type].append(task.condition_value)

        elif task.operation_type == "remove":
            if isinstance(state.conditions.get(condition_type), list):
                try:
                    state.conditions[condition_type].remove(task.condition_value)
                except ValueError:
                    pass

        state.pending_tasks.remove(task)

    state.response_text = "요청하신 조건을 반영했습니다."
    return state
