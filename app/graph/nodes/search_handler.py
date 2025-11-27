# app/graph/nodes/search_handler.py
from app.graph.state import ChatState
from app.db.database import PostgresDB

db = PostgresDB()

def search_handler(state: ChatState) -> ChatState:
    if not state.conditions or all(v in [None, [], ""] for v in state.conditions.values()):
        state.response_text = "검색할 조건이 없습니다."
        return state

    try:
        query = "SELECT * FROM jobs LIMIT 5;"
        rows = db.execute_query(query)
        state.search_result = rows
        state.response_text = f"{len(rows)}개의 공고를 찾았습니다." if rows else "조건에 맞는 공고가 없습니다."
    except Exception as e:
        state.error.append(str(e))
        state.response_text = "검색 중 오류가 발생했습니다."

    return state
