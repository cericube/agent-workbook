# 소스 경로: gemini-sdk-basics/ch04/function_calling.py
"""조회 함수와 도구 스키마를 불러와 Gemini Function Calling 실습을 실행합니다."""

import os

from customer_tools import get_customer, get_customer_tool
from delivery_tools import get_delivery_status, get_delivery_status_tool
from dotenv import load_dotenv
from eta_tools import get_delivery_eta, get_delivery_eta_tool
from google import genai
from google.genai.interactions import (
    FunctionCallStep,
    FunctionParam,
    FunctionResultStepParam,
    Interaction,
)
from order_tools import get_order, get_order_tool
from return_tools import get_return_policy, get_return_policy_tool


def ask_question(client: genai.Client, model: str, question: str):
    """함수 호출 요청 → Python 실행 → 결과 전달을 반복합니다."""
    # 전체 흐름: 1~3 준비와 첫 요청 → 4~10 응답 확인과 반복 호출 → 11~12 완료 확인과 출력.
    # 1. 모델이 선택할 도구 설명을 준비합니다. 실제 함수는 7번에서 Python이 실행합니다.
    tools: list[FunctionParam] = [
        get_customer_tool,
        get_order_tool,
        get_delivery_status_tool,
        get_delivery_eta_tool,
        get_return_policy_tool,
    ]
    print("\n사용자 질문:", question)
    # 2. 질문마다 횟수를 새로 셉니다. API 요청 수, 도구 처리 회차, 함수 실행 건수는 다릅니다.
    api_requests = 1
    tool_round = 0
    function_count = 0
    # 여섯 회차의 결과 전달 후에도 호출 요청이 남아 있으면 6번에서 중단합니다.
    max_tool_rounds = 6

    # 3. 질문과 도구 설명으로 첫 API 요청을 보냅니다. 아직 Python 함수는 실행하지 않습니다.
    print("[API 요청 1] 질문과 도구 설명 전달")
    # 각 질문은 이전 응답 ID 없이 새 대화로 시작합니다.
    response = client.interactions.create(
        model=model,
        input=question,
        tools=tools,
        stream=False,  # 스트리밍 이벤트 대신 응답 객체를 받습니다.
        store=True,  # 후속 요청에서 이전 응답 ID를 참조할 수 있게 기록을 저장합니다.
    )

    # 4. 첫 응답과 10번에서 받은 후속 응답을 같은 반복문에서 검사합니다.
    # 도구 개수만큼 반복하는 것이 아닙니다. 5번에서 호출 요청이 없으면 종료합니다.
    while True:
        if not isinstance(response, Interaction):
            raise TypeError("일반 응답이 필요합니다.")
        # 일반 완료 상태와 도구 실행을 기다리는 상태의 응답을 처리합니다.
        if response.status not in ("completed", "requires_action"):
            raise RuntimeError(f"요청 실패: {response.status}")
        # 5. 응답에서 함수 호출 요청을 모읍니다. 모델은 함수 이름과 인자만 요청합니다.
        calls = [
            step for step in response.steps or [] if isinstance(step, FunctionCallStep)
        ]
        if not calls:
            # 추가 실행할 함수가 없으면 while을 벗어나 11번의 완료 검증으로 이동합니다.
            # 호출 요청이 없다는 사실만으로 정상 완료가 보장되지는 않습니다.
            print(f"[API 응답 {api_requests}] 함수 호출 없음 → 최종 답변 확인")
            break
        # 6. 호출 요청이 남아 있으면 회차 상한을 확인합니다. 초과 시 답변 대신 오류로 종료합니다.
        if tool_round >= max_tool_rounds:
            raise RuntimeError("도구 실행 회차 제한을 초과했습니다.")

        tool_round += 1
        print(f"[도구 회차 {tool_round}] 호출 요청 {len(calls)}개")
        # 7. 이번 응답의 호출들을 Python에서 하나씩 실행합니다.
        # 한 회차에 호출이 여러 개일 수 있으므로 회차 수와 함수 실행 건수는 다를 수 있습니다.
        results: list[FunctionResultStepParam] = []
        # 여러 호출도 이 for문에서는 순서대로 실행합니다. 동시에 실행하는 코드는 아닙니다.
        for call in calls:
            # **는 인자 딕셔너리를 함수의 키워드 인자로 풀어 줍니다.
            if call.name == "get_customer":
                result = get_customer(**call.arguments)
            elif call.name == "get_order":
                result = get_order(**call.arguments)
            elif call.name == "get_delivery_status":
                result = get_delivery_status(**call.arguments)
            elif call.name == "get_delivery_eta":
                result = get_delivery_eta(**call.arguments)
            elif call.name == "get_return_policy":
                result = get_return_policy(**call.arguments)
            else:
                raise ValueError(f"등록하지 않은 도구입니다: {call.name}")
            function_count += 1
            print("  실행:", call.name, call.arguments)
            print("  결과:", result)
            # 8. 각 실행 결과를 results에 모읍니다. 이 단계에서는 API를 호출하지 않습니다.
            # call.id로 어느 함수 호출의 결과인지 연결합니다.
            # 남은 호출이 있으면 7번의 for 반복으로 돌아가 계속 실행합니다.
            results.append(
                {
                    "type": "function_result",
                    "name": call.name,
                    "call_id": call.id,
                    # 조회 결과를 텍스트 목록으로 전달합니다.
                    "result": [{"type": "text", "text": result}],
                }
            )

        # 9. 이번 회차의 모든 함수를 실행한 뒤 이전 응답 ID를 확인합니다.
        # response.id는 대화를 연결하고, 8번의 call.id는 개별 호출과 결과를 연결합니다.
        if not response.id:
            raise RuntimeError("이전 응답 ID가 없습니다.")
        api_requests += 1
        print(f"[API 요청 {api_requests}] 도구 결과 전달 → 다음 응답 받기")
        # 10. 모아 둔 결과와 도구 설명을 모델에 보내고 response를 새 응답으로 교체합니다.
        # 모델은 결과를 보고 추가 함수 호출 또는 최종 답변을 선택합니다.
        # 요청이 끝나면 4번으로 돌아갑니다. 추가 호출이 있으면 6~10번을 다시 수행합니다.
        response = client.interactions.create(
            model=model,
            input=results,
            previous_interaction_id=response.id,
            tools=tools,
            stream=False,
            store=True,
        )

    # 11. 5번의 break로 나온 뒤 완료 상태와 답변 텍스트를 확인합니다.
    # 두 조건을 만족하지 않으면 정상 답변으로 출력하지 않고 오류를 알립니다.
    if response.status != "completed" or not response.output_text:
        raise RuntimeError(f"최종 답변을 받지 못했습니다: {response.status}")
    # 12. 최종 답변과 실행 횟수를 출력하고 main()의 다음 질문으로 돌아갑니다.
    print("Gemini 답변:", response.output_text)
    print(
        f"[실행 요약] API 요청 {api_requests}회 / "
        f"도구 처리 {tool_round}회차 / 함수 실행 {function_count}건"
    )


def main():
    # .env의 값을 환경 변수로 불러옵니다. 이미 설정된 값은 그대로 사용합니다.
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY") or not os.environ.get("GEMINI_MODEL"):
        raise RuntimeError(".env에 GEMINI_API_KEY와 GEMINI_MODEL을 설정해 주세요.")
    model = os.environ["GEMINI_MODEL"]

    # 실행 순서: main() → 질문마다 ask_question()의 1~12번 → 다음 질문 → 연결 종료.
    # 같은 처리 코드로 단일 호출, 연속 호출, 여러 호출을 비교합니다.
    # 아래 흐름은 예상 예시이며, 실제 호출 순서와 묶음은 모델 응답에 따라 달라집니다.
    questions = [
        # 단일 호출: 주문 조회
        "주문번호 ORD-1001의 상품이 뭐야?",
        # 연속 호출: 주문 조회 → 배송 조회
        "주문번호 ORD-1001의 배송 상태를 알려 줘.",
        # 긴 연속 호출: 고객 조회 → 주문 조회 → 배송 조회 → 도착 예정일 조회
        "고객 ID CUST-001의 최근 주문은 언제 도착해?",
        # 여러 정보: 주문 조회 후 배송 조회와 반품 조건 조회를 함께 요청할 수도 있습니다.
        "주문번호 ORD-1001의 배송 상태와 반품 조건을 알려 줘.",
    ]
    with genai.Client() as client:
        for number, question in enumerate(questions, start=1):
            print(f"\n===== 실습 {number} =====")
            # 이 질문의 반복 호출과 완료 처리가 끝나면 다음 질문을 시작합니다.
            # 예외가 발생하면 다음 질문으로 진행하지 않고 with를 벗어나 연결을 닫습니다.
            ask_question(client, model, question)
    # 블록을 벗어나면 연결을 닫습니다. 서버 기록을 삭제하는 것은 아닙니다.


if __name__ == "__main__":
    # import할 때는 요청을 보내지 않고, 직접 실행할 때만 네 질문을 수행합니다.
    main()
