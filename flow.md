```mermaid
flowchart TD
    %% === Entry ===
    A[entry_router] -->|pending 없음| B[intent_normal]
    A -->|pending 있음| C[intent_clarification]

    %% === Intent Normal ===
    B --> D[post_intent_router]

    %% === Intent Clarification ===
    C -->|답변 포함| E[clarification_handler]
    C -->|답변 아님| D

    %% === Clarification Handler ===
    E --> D

    %% === Post Intent Router ===
    D -->|intent_has_modify_request==True| F[condition_modify_handler]
    D -->|intent_has_condition_text==True| G[condition_add_handler]
    D -->|modify/add 모두 없음| X[finalize_and_route]

    %% === Condition Modify Handler ===
    F -->|intent_has_condition_text == True| G
    F -->|intent_has_condition_text == False| X

    %% === Condition Add Handler ===
    G -->|intent_has_modify_request == False| X

    %% === Finalize and Route ===
    X -->|조건 미완료| Z1["END - clarification 질문 출력"]
    X -->|조건 완료 AND intent_want_search == True| H[search_handler]
    X -->|조건 완료 AND intent_want_search == False| Z2["END - 조건 반영 완료 응답"]

    %% === Search Handler ===
    H --> Z2
