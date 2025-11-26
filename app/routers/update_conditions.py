from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from openai import OpenAI
import json

router = APIRouter()

# 간단한 in-memory 대화 기록 저장소
# 구조: { user_id: [ {role, content}, ... ] }
conversation_store: Dict[str, List[Dict[str, str]]] = {}


class LLMClient:
    """
    OpenAI LLM 호출용 아주 얇은 래퍼.
    - response_format=json_object 로 강제
    - JSON 문자열을 파싱해 dict 로 반환
    """

    def __init__(self):
        self.client = OpenAI()

    def chat_json(self, *, messages: List[Dict[str, str]], model: str = "gpt-5-nano") -> Dict[str, Any]:
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
            )
        except Exception as e:
            raise RuntimeError(f"LLM 호출 실패: {e}")

        content = completion.choices[0].message.content
        if not content:
            raise RuntimeError("LLM 응답이 비어 있습니다.")

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"LLM가 유효한 JSON 을 반환하지 않았습니다: {e}\n원본: {content}")


llm = LLMClient()


from pydantic import field_validator

class ConditionUpdateRequest(BaseModel):
    userId: Optional[str] = "anonymous"
    text: str
    condition: Dict[str, Any] = {}
    search: bool = False

    @field_validator("userId", mode="before")
    def default_user_id(cls, v):
        return v or "anonymous"

class ConditionUpdateResponse(BaseModel):
    success: bool
    state: Dict[str, Any]


@router.post("/", response_model=ConditionUpdateResponse)
def update_conditions(request: ConditionUpdateRequest) -> ConditionUpdateResponse:
    system_prompt = """
너는 단기 알바 조건 수집 챗봇이다. 간결하고 정중하게 응답한다. 
먼저, 사용자가 검색을 원하는지 판단 후 want_search 여부를 결정하고, 
사용자의 알바 조건을 수집하면서 사용자의 입력에 대한 자연스러운 응답을 생성한다.
대화가 알바 조건 수집과 관련이 없으면, 정중하게 알바 조건에 대해 물어봐라.

목적
- 사용자가 검색을 원하는지 판단해 want_search 값을 true/false 로 설정한다.
- 사용자의 입력과 기존 조건을 참고하여 최종 업데이트된 condition을 생성한다. 
- 응답 구조의 모든 키를 포함하며, 빈 값도 Null로 채운다.
- job_text 와 person_text는 서로 분리해 사용자가 제공한 텍스트 중 condition에 해당하지 않는 일/사람에 관련된 텍스트의 원문을 최대한 유지한 형태로 job_text는 업무에 대한 서술의 형태, person_text는 사람에 대한 서술의 형태로 작성한다.
- 사용자가 명확히 언급하지 않은 조건은 기존 condition에서 가져온다.
- 자연어 응답은 llm_response에 넣고, JSON 외 텍스트는 절대 포함하지 마라.

place는 다음 목록에 포함된 값의 배열로[ { "region1": "서울", "region2": "강남구" },... ] 형태로 작성한다.
place 목록:
{
  "서울": [
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구",
    "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구",
    "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구",
    "종로구", "중구", "중랑구"
  ],
  "부산": [
    "강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구", "북구",
    "사상구", "사하구", "서구", "수영구", "연제구", "영도구", "중구", "해운대구"
  ],
  "대구": [
    "군위군", "남구", "달서구", "달성군", "동구", "북구", "서구", "수성구", "중구"
  ],
  "인천": [
    "강화군", "계양구", "미추홀구", "남동구", "동구", "부평구", "서구", "연수구", "옹진군", "중구"
  ],
  "광주": [
    "광산구", "남구", "동구", "북구", "서구"
  ],
  "대전": [
    "대덕구", "동구", "서구", "유성구", "중구"
  ],
  "울산": [
    "남구", "동구", "북구", "울주군", "중구"
  ],
  "세종": [],
  "경기": [
    "가평군", "고양시 덕양구", "고양시 일산동구", "고양시 일산서구", "과천시", "광명시",
    "광주시", "구리시", "군포시", "김포시", "남양주시", "동두천시",
    "부천시 소사구", "부천시 오정구", "부천시 원미구",
    "성남시 분당구", "성남시 수정구", "성남시 중원구",
    "수원시 권선구", "수원시 영통구", "수원시 장안구", "수원시 팔달구",
    "시흥시", "안산시 단원구", "안산시 상록구", "안성시",
    "안양시 동안구", "안양시 만안구", "양주시", "양평군", "여주시", "연천군",
    "오산시", "용인시 기흥구", "용인시 수지구", "용인시 처인구",
    "의왕시", "의정부시", "이천시", "파주시", "평택시",
    "포천시", "하남시", "화성시"
  ],
  "경남": [
    "거제시", "거창군", "고성군", "김해시", "남해군", "밀양시",
    "사천시", "산청군", "양산시", "의령군", "진주시", "창녕군",
    "창원시 마산합포구", "창원시 마산회원구",
    "창원시 성산구", "창원시 의창구", "창원시 진해구",
    "통영시", "하동군", "함안군", "함양군", "합천군"
  ],
  "경북": [
    "경산시", "경주시", "고령군", "구미시", "김천시",
    "문경시", "봉화군", "상주시", "성주군", "안동시",
    "영덕군", "영양군", "영주시", "영천시", "예천군",
    "울릉군", "울진군", "의성군", "청도군", "청송군",
    "칠곡군", "포항시 남구", "포항시 북구"
  ],
  "충남": [
    "계룡시", "공주시", "금산군", "논산시", "당진시",
    "보령시", "부여군", "서산시", "서천군", "아산시",
    "연기군", "예산군",
    "천안시 동남구", "천안시 서북구",
    "청양군", "태안군", "홍성군"
  ],
  "충북": [
    "괴산군", "단양군", "보은군", "영동군", "옥천군",
    "음성군", "제천시", "증평군", "진천군",
    "청주시 상당구", "청주시 흥덕구", "청주시 서원구", "청주시 청원구",
    "충주시"
  ],
  "전남": [
    "강진군", "고흥군", "곡성군", "광양시", "구례군",
    "나주시", "담양군", "목포시", "무안군", "보성군",
    "순천시", "신안군", "여수시", "영광군", "영암군",
    "완도군", "장성군", "장흥군", "진도군",
    "함평군", "해남군", "화순군"
  ],
  "전북": [
    "고창군", "군산시", "김제시", "남원시", "무주군",
    "부안군", "순창군", "완주군", "익산시", "임실군",
    "장수군", "전주시 덕진구", "전주시 완산구",
    "정읍시", "진안군"
  ],
  "강원": [
    "강릉시", "고성군", "동해시", "삼척시", "속초시",
    "양구군", "양양군", "영월군", "원주시", "인제군",
    "정선군", "철원군", "춘천시", "태백시", "평창군",
    "홍천군", "화천군", "횡성군"
  ],
  "제주": [
    "서귀포시",
    "제주시"
  ]
}

categoties는 다음 목록에 포함된 값의 배열로[{ "category1": "병원·간호·연구", "category2": "생동성·임상시험" }, ... ] 형태로 작성한다.
categories 목록:
{
  "외식·음료": [
    "일반음식점",
    "레스토랑",
    "패밀리레스토랑",
    "패스트푸드",
    "치킨·피자전문점",
    "커피전문점",
    "아이스크림·디저트",
    "베이커리·도넛·떡",
    "호프·일반주점",
    "바(Bar)",
    "급식·푸드시스템",
    "도시락·반찬"
  ],
  "유통·판매": [
    "백화점·면세점",
    "복합쇼핑몰·아울렛",
    "쇼핑몰·소셜커머스·홈쇼핑",
    "대형마트",
    "편의점",
    "의류·잡화매장",
    "뷰티·헬스스토어",
    "휴대폰·전자기기매장",
    "가구·침구·생활소품",
    "서점·문구·팬시",
    "약국",
    "농수산·청과·축산",
    "화훼·꽃집",
    "유통·판매 기타"
  ],
  "문화·여가·생활": [
    "놀이공원·테마파크",
    "호텔·리조트·숙박",
    "여행·캠프·레포츠",
    "영화·공연",
    "전시·컨벤션·세미나",
    "독서실·고시원·스터디룸",
    "PC방",
    "노래방",
    "볼링·당구장",
    "스크린골프·야구",
    "DVD·만화카페·멀티방",
    "오락실·게임장",
    "이색테마카페",
    "키즈카페",
    "찜질방·사우나·스파",
    "피트니스·스포츠",
    "공인중개",
    "골프캐디",
    "고속도로휴게소",
    "문화·여가·생활 기타"
  ],
  "서비스": [
    "매장관리·판매",
    "MD",
    "캐셔·카운터",
    "서빙",
    "주방장·조리사",
    "주방보조·설거지",
    "바리스타",
    "안내데스크·매표",
    "주차관리·주차도우미",
    "보안·경비·경호",
    "주유·세차",
    "전단지배포",
    "청소·미화",
    "렌탈관리·A/S",
    "헤어·미용·네일관리",
    "마사지",
    "반려동물케어",
    "베이비시터·가사도우미",
    "결혼·연회·장례도우미",
    "판촉도우미",
    "이벤트·행사스텝",
    "나레이터모델",
    "피팅모델",
    "피부관리",
    "서비스 기타"
  ],
  "사무·회계": [
    "사무보조",
    "문서작성·자료조사",
    "비서",
    "회계·경리",
    "인사·총무",
    "마케팅·광고·홍보",
    "번역·통역",
    "복사·출력·제본",
    "편집·교정·교열",
    "공공기관·공기업·행정",
    "학교·도서관·교육기관"
  ],
  "고객상담·영업·리서치": [
    "고객상담·인바운드",
    "텔레마케팅·아웃바운드",
    "금융·보험영업",
    "일반영업·판매",
    "설문조사·리서치",
    "영업관리·지원"
  ],
  "생산·건설·노무": [
    "제조·가공",
    "포장·품질검사",
    "입출고·창고관리",
    "상하차·소화물분류",
    "전기·전자·가스",
    "정비·수리·A/S",
    "공사·건설현장",
    "닥트·배관설치",
    "조선소",
    "생산·건설·노무 기타"
  ],
  "IT·인터넷": [
    "웹·모바일기획",
    "사이트·콘텐츠운영",
    "바이럴·SNS마케팅",
    "프로그래머",
    "HTML코딩",
    "QA·테스터·검증",
    "시스템·네트워크·보안",
    "PC·디지털기기 설치·관리"
  ],
  "교육·강사": [
    "입시·보습학원",
    "외국어·어학원",
    "컴퓨터·정보통신",
    "요가·필라테스 강사",
    "피트니스 트레이너",
    "레져스포츠 강사",
    "예체능 강사",
    "유아·유치원 교사",
    "방문·학습지 교사",
    "보조교사",
    "자격증·기술학원 강사",
    "대학·교육기관 강사",
    "교육·강사 기타"
  ],
  "디자인": [
    "웹·모바일디자인",
    "그래픽·편집디자인",
    "제품·산업디자인",
    "CAD·CAM·인테리어",
    "캐릭터·애니메이션디자인",
    "패션·잡화디자인",
    "디자인 기타"
  ],
  "미디어": [
    "보조출연·방청",
    "방송스텝·촬영보조",
    "동영상촬영·편집",
    "사진촬영·편집",
    "조명·음향",
    "방송사·프로덕션",
    "신문·잡지·출판",
    "미디어 기타"
  ],
  "운전·배달": [
    "운반·이사",
    "대리운전·일반운전",
    "택시·버스운전",
    "수행기사",
    "화물·중장비·특수차",
    "택배·퀵서비스",
    "배달"
  ],
  "병원·간호·연구": [
    "간호사·간호조무사",
    "간병·사회복지사",
    "코디네이터·원무",
    "병동·외래보조",
    "수의사·수의간호사",
    "실험·연구보조",
    "생동성·임상시험"
  ]
}

work_days는 ISO 날짜 형식(YYYY-MM-DD)인 문자열의 배열로 작성한다.
start_time, end_time은 24시간 형식(HH:MM)으로 작성한다.
hourly_wage는 한화를 기준으로 숫자(0 이상의 정수)로 작성한다.
gender는 "무관", "남성", "여성" 중 하나로 작성한다.
age는 0 이상의 정수로 작성한다.

응답 형식
반드시 아래 JSON 구조만 반환하라. 키 이름 변경 금지.
{
  "updated_conditions": {
        "place": null,
        "categories": null,
        "work_days": null,
        "start_time": null,
        "end_time": null,
        "hourly_wage": null,
        "gender": null,
        "age": null,
        "job_text": null,
        "person_text": null
    },
  "llm_response": "사용자에게 보여줄 자연어 응답",
  "want_search": true/false
}

설명 문장 포함 금지. JSON만 반환.
"""

    # 유저별 대화 기록 불러오기, 없으면 초기화
    user_history = conversation_store.get(request.userId, [])

    user_prompt = f"""
[대화 히스토리]
{json.dumps(user_history, ensure_ascii=False, indent=2)}

[기존 Conditions]
{json.dumps(request.condition, ensure_ascii=False, indent=2)}

[사용자 입력]
{request.text}
"""

    # LLM 호출 메시지 구성
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        result = llm.chat_json(messages=messages, model="gpt-5-mini")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    print("\n🔎 LLM RAW RESULT:\n", result, "\n")

    updated_conditions = result.get("updated_conditions", {}) or {}
    llm_response_text = result.get("llm_response", "")
    json_response_text = json.loads(json.dumps(result))

    # 유저 대화 기록 업데이트 (request 입력 + LLM 응답)
    user_history.append({"role": "user", "content": request.text})
    user_history.append({"role": "assistant", "content": llm_response_text})
    conversation_store[request.userId] = user_history

    expected_keys = [
        "place",
        "categories",
        "work_days",
        "start_time",
        "end_time",
        "hourly_wage",
        "gender",
        "age",
        "job_text",
        "person_text",
    ]

    return ConditionUpdateResponse(
        success=True,
        state={
            "condition": updated_conditions,
            "llm_response": llm_response_text
        }
    )
