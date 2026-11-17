# 소스 경로: gemini-sdk-basics/ch02/02_interactions_conversation.py
"""2–3. store=True와 previous_interaction_id로 서버 대화 연결."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.interactions import (
    Interaction,
    ModelOutputStep,
    TextContent,
    UserInputStep,
)


def delete_interactions(client: genai.Client, interaction_ids: list[str]) -> None:
    """서버 기록을 최신 턴부터 삭제하고, 성공한 ID는 전달받은 목록에서도 제거합니다."""
    # 삭제한 ID를 원본 목록에서 제거하므로, 복사본을 만들어 최신 ID부터 순회합니다.
    # 삭제 중 오류가 나면 예외를 그대로 전달하고, 아직 삭제하지 못한 ID는 목록에 남깁니다.
    for interaction_id in reversed(interaction_ids.copy()):
        client.interactions.delete(interaction_id)
        interaction_ids.remove(interaction_id)
        print("삭제한 ID:", interaction_id)


# .env의 값을 환경 변수로 불러옵니다. 기존 환경 변수는 기본적으로 덮어쓰지 않습니다.
load_dotenv()

# 설정의 누락이나 빈 값을 확인합니다. API 키의 유효성이나 모델 접근 권한 검사는 아닙니다.
if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError(".env 파일에 GEMINI_API_KEY를 설정해 주세요.")
if not os.environ.get("GEMINI_MODEL"):
    raise RuntimeError(".env 파일에 GEMINI_MODEL을 설정해 주세요.")
model = os.environ["GEMINI_MODEL"]

# 모델의 역할과 답변 방식은 system_instruction에, 질문은 input에 지정합니다.
system_instruction = "당신은 Python 입문 강사입니다. 한국어로 짧고 쉽게 답하세요."


# 환경 변수의 API 키를 사용하며, 대화 생성·조회·삭제 요청은 각 메서드를 호출할 때 보냅니다.
client = genai.Client(
    http_options=types.HttpOptions(
        # HTTP 요청 제한 시간은 밀리초 단위입니다. 60_000은 60초입니다.
        timeout=60_000,
        retry_options=types.HttpRetryOptions(
            # 재시도 대상 오류가 발생하면 최초 요청을 포함해 최대 3번 시도합니다.
            attempts=3,
            # 재시도 대기 시간은 초 단위입니다.
            initial_delay=1.0,
            # 재시도 사이에는 최대 10초까지 기다립니다. 전체 실행 시간을 제한하는 값은 아닙니다.
            max_delay=10.0,
            # 요청 시간 초과, 호출 한도 초과, 일시적인 서버 오류가 발생하면 다시 요청합니다.
            http_status_codes=[408, 429, 500, 502, 503, 504],
        ),
    ),
)

# 조회와 삭제에 사용할 ID를 보관합니다. 오류가 발생해도 finally에서 접근할 수 있습니다.
interaction_ids = []

try:
    # 아직 연결할 이전 응답이 없으므로 첫 요청은 새 대화로 시작합니다.
    print("\n############# 멀티 턴 대화 #############\n")
    previous_id = None
    for question in [
        "저는 민수이고 Python 리스트를 공부합니다.",
        "제 이름과 공부 주제를 기억하나요?",
        "그 주제로 연습 문제 하나를 주세요.",
    ]:
        # 첫 요청에는 이전 응답 ID를 넣지 않고, 다음 요청부터 직전 응답 ID를 전달합니다.
        # 이전 ID는 대화 이력만 연결하므로 역할과 응답 지침은 매 요청에 다시 전달합니다.
        if previous_id is None:
            interaction = client.interactions.create(
                model=model,
                input=question,
                # 같은 역할과 답변 방식을 유지하도록 이번 요청에도 지침을 전달합니다.
                system_instruction=system_instruction,
                # 입력과 응답을 서버에 저장해 이후 ID 연결과 조회에 사용합니다.
                store=True,
                # 스트리밍 이벤트 대신 완성된 Interaction 객체를 받습니다.
                stream=False,
            )
        else:
            interaction = client.interactions.create(
                model=model,
                input=question,
                # 같은 역할과 답변 방식을 유지하도록 이번 요청에도 지침을 전달합니다.
                system_instruction=system_instruction,
                store=True,
                stream=False,
                # 서버에 저장된 이전 대화를 바탕으로 이번 질문에 답하도록 응답 ID를 전달합니다.
                previous_interaction_id=previous_id,
            )
        # 반환값이 일반 응답 객체인지 확인합니다. Pylance도 이 검사로 응답의 타입을 판단합니다.
        if not isinstance(interaction, Interaction):
            raise TypeError("일반 Interaction 응답이 필요합니다.")
        # 답변이 정상적으로 완료됐고 ID가 있어야 다음 질문을 이어 갑니다.
        # ID가 없거나 비어 있으면 다음 질문을 연결할 수 없으므로 실행을 중단합니다.
        if interaction.status != "completed" or not interaction.id:
            raise RuntimeError(f"대화가 완료되지 않았습니다: {interaction.status}")
        interaction_ids.append(interaction.id)
        # 매번 최신 ID로 갱신해야 다음 질문이 방금 끝난 응답에서 이어집니다.
        previous_id = interaction.id
        print("사용자:", question)
        print("모델:", interaction.output_text or "텍스트 응답이 없습니다.")
        print("다음 턴에 전달할 ID:", previous_id)

    print("\n############# 대화 완료 후 서버 기록 조회 #############\n")
    # 대화가 끝나면 서버에 저장된 각 기록을 다시 조회해 출력합니다.
    for interaction_id in interaction_ids:
        # 로컬 목록에는 ID만 있고, 대화 내용은 서버에서 다시 가져옵니다.
        stored = client.interactions.get(interaction_id)
        if not isinstance(stored, Interaction):
            raise TypeError("일반 Interaction 응답이 필요합니다.")
        print("\n조회한 ID:", stored.id)
        # steps는 사용자 입력, 모델 출력, 사고 과정 등으로 구성됩니다.
        # 단계 목록이 없으면 빈 목록을 순회해 출력 없이 넘어갑니다.
        for step in stored.steps or []:
            # 이 실습에서는 사용자 입력과 모델 출력 단계만 확인합니다.
            if isinstance(step, (UserInputStep, ModelOutputStep)):
                for content in step.content or []:
                    # 한 단계에 여러 콘텐츠가 있을 수 있으므로 텍스트만 골라 출력합니다.
                    if isinstance(content, TextContent):
                        print(f"[{step.type}] {content.text}")

    print("\n############# 서버저장 옵션 제거 후 질문 #############\n")
    # 이전 ID를 생략하면 앞서 입력한 이름과 공부 주제가 이 요청에 전달되지 않습니다.
    # 두 번째 턴과 같은 질문을 보내 연결된 대화와 새 대화의 응답을 비교합니다.
    fresh = client.interactions.create(
        model=model,
        input="제 이름과 공부 주제를 기억하나요?",
        system_instruction=system_instruction,
        stream=False,
        # 이 비교 요청은 이후 조회하거나 이어 쓰지 않으므로 서버 저장을 끕니다.
        store=False,
    )
    if not isinstance(fresh, Interaction):
        raise TypeError("일반 Interaction 응답이 필요합니다.")
    if fresh.status != "completed":
        raise RuntimeError(f"응답이 완료되지 않았습니다: {fresh.status}")
    print("\n[이전 ID 없이 시작한 새 대화]")
    print(fresh.output_text or "텍스트 응답이 없습니다.")
    # store=False로 생성한 응답은 이후 대화 연결에 사용할 수 없습니다.
except Exception as error:
    # try 블록에서 발생한 오류를 출력한 뒤 다시 발생시켜 호출한 쪽에도 오류를 알립니다.
    print("오류:", type(error).__name__, str(error))
    raise
finally:
    try:
        # 더 이상 삭제한 대화를 연결하지 않도록 이전 ID를 초기화합니다.
        print("\n############# 대화 서버 기록 삭제 #############\n")
        previous_id = None
        delete_interactions(client, interaction_ids)
    finally:
        # 삭제 도중 오류가 발생해도 HTTP 연결 자원은 정리합니다.
        client.close()
