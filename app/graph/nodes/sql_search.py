from app.db.database import PostgresDB

db = PostgresDB()

def sql_search(state):
    print("[sql_search] 실행됨")

    # 일반 SQL 검색이 정확(정밀)하게 되는 것만 조건으로 넣어야 할 것임 (UI에서부터) : 아래 경우 검색 속도가 문제가 되거나 까다로운 경우가 있음 (예: 지역)
    gender = state.condition.get("gender") # 알바가 남자일 경우 일자리 매칭은 남자 또는 성별 무관으로 검색해야 함
    age = state.condition.get("age") # 알바가 30세이면 일자리 매칭은 30세 전후 + 알파값(예:+-5)으로 검색해야 함
    place = state.condition.get("place") # 알바가 수원이면 버스 이동 기준으로 인근 10km반경 또는 지역 무관으로 검색해야 함 (예: 경기도일 경우 복잡해짐)
    work_days = state.condition.get("work_days") # 알바가 일자를 지정하는 것은 어렵고 차라리 요일로만 받거나 요일 무관으로 검색해야 함 (배열)
    start_time = state.condition.get("start_time") # 알바가 start_time과 end_time 2개의 조합으로 또는 근무시간 무관으로 검색해야 함
    end_time = state.condition.get("end_time") # 상동
    hourly_wage = state.condition.get("hourly_wage") # 알바가 원하는 시급 전후 알파값으로 검색해야 함
    requirements = state.condition.get("requirements") # 알바가 가진 장점과 사업주가 요구하는 조건이 하나라도 맞는 것을 검색해야 함 (배열) 
    category = state.condition.get("category") # 알바가 생각하는 직종(카테고리)와 사업주가 적은 것과 LLM이 판단한 직종(카테고리)이 다를 수 있음

    # 위 내용을 단기간에 SQL로 검색하는 것을 정확하게 구현하는 것은 프로젝트 일정에 맞추기 어려울 것임 (일반 SQL은 나중에 기회되면 고려)
    # 차라리, 일반SQL 검색은 없애고 벡터 검색으로 1) 조건으로 검색 2) 채팅(자연어)로만 검색 두가지로 제공하는 것을 고민하기
    # 이 때, 1)의 조건으로 검색을 위해서 공고 저장시 각 필드들을 임베딩 대상으로 포함해 저장하기로 함
    # 현재 LangGraph 분기는 변경없이 그대로 가면 되고 sql_search.py만 제거되고 vector_search.py로 통합됨 (react에서 검색text만 구분되어 넘어올 것임)
    # 그런데, 현재 필드값 other_requirement와 requirements가 혼란스럽게 사용중 (이 부분을 정리해야 의도한 검색이 정밀해 질 것임)
    # => 사업주 공고등록시 임베딩 대상 필드 및 알바의 일자리 검색시 요청하는 자연어 조건과 매칭되어야 함

    # 라디오 및 버튼 이름 정리 => 아래 2가지가 라디오 옵션으로 제공되며 선택시 해당 이름으로 버튼 이름이 변경됨
    # 1. 조건 추가
    # 2. 조건으로 검색 => 채팅 메시지 내용이 없으면 '조건으로 검색', 있으면 '채팅으로 검색'으로 바로바로 표시
    
    # RQ 파라미터도 변경 사항 없이 코딩만 추가 

    # 사이트 정체성 => 알바 (gigwork로 도메인 구매. 최소 1년 유지)

    query = """
        SELECT id, company, description, location, salary, status, title, work_days, work_hours, end_time, 
               other_requirement, qualifications, requirements, salary_type, start_time, category, age, education, gender
        FROM jobs
        WHERE 
        ORDER BY 최근공지부터
    """

    params = (embedding_str, embedding_str, similarity_threshold, embedding_str, limit)

    try:
        rows = db.execute_query(query, params)
        print(f'rows######################{rows}')
    except Exception as e:
        print(f'e$$$$$$$$$$$$$$$$$$$$$$$$$$${e}')
        state.response = f"DB 검색 중 오류 발생: {e}"
        state.result = []
        return state
    finally:
        db.close()

    state.result = rows
    state.response = f"일반 SQL 검색으로 {len(rows)}개의 알바를 찾았습니다."

    return state