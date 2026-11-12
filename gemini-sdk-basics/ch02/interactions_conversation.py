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

# ch01과 같이 .env에서 API 키와 모델 이름을 읽습니다.
load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError(".env 파일에 GEMINI_API_KEY를 설정해 주세요.")
if not os.environ.get("GEMINI_MODEL"):
    raise RuntimeError(".env 파일에 GEMINI_MODEL을 설정해 주세요.")
model = os.environ["GEMINI_MODEL"]

# 역할과 응답 형식은 지침에, 이번에 해결할 질문은 사용자 입력에 둡니다.
system_instruction = "당신은 Python 입문 강사입니다. 한국어로 짧고 쉽게 답하세요."


client = genai.Client(
    http_options=types.HttpOptions(timeout=60_000),
)

try:
    interaction_ids = []
    previous_id = None
    for question in [
        "저는 민수이고 Python 리스트를 공부합니다.",
        "제 이름과 공부 주제를 기억하나요?",
        "그 주제로 연습 문제 하나를 주세요.",
    ]:
        # 첫 요청은 이전 ID 없이, 후속 요청은 직전 ID를 지정합니다.
        # System Instruction은 매 요청에 다시 전달합니다.
        if previous_id is None:
            interaction = client.interactions.create(
                model=model,
                input=question,
                system_instruction=system_instruction,
                store=True,
                stream=False,
            )
        else:
            interaction = client.interactions.create(
                model=model,
                input=question,
                system_instruction=system_instruction,
                store=True,
                stream=False,
                previous_interaction_id=previous_id,
            )
        if not isinstance(interaction, Interaction):
            raise TypeError("일반 Interaction 응답이 필요합니다.")
        if interaction.status != "completed" or not interaction.id:
            raise RuntimeError(f"대화가 완료되지 않았습니다: {interaction.status}")
        interaction_ids.append(interaction.id)
        previous_id = interaction.id
        print("사용자:", question)
        print("모델:", interaction.output_text or "텍스트 응답이 없습니다.")
        print("다음 턴에 전달할 ID:", previous_id)

    # 각 턴을 조회해 실제 저장된 사용자 입력과 모델 출력을 확인합니다.
    for interaction_id in interaction_ids:
        stored = client.interactions.get(interaction_id)
        if not isinstance(stored, Interaction):
            raise TypeError("일반 Interaction 응답이 필요합니다.")
        print("\n조회한 ID:", stored.id)
        for step in stored.steps or []:
            if isinstance(step, (UserInputStep, ModelOutputStep)):
                for content in step.content or []:
                    if isinstance(content, TextContent):
                        print(f"[{step.type}] {content.text}")

    # 같은 질문을 이전 ID 없이 보내 새 대화가 시작되는지 비교합니다.
    fresh = client.interactions.create(
        model=model,
        input="제 이름과 공부 주제를 기억하나요?",
        system_instruction=system_instruction,
        stream=False,
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
    print("오류:", type(error).__name__, str(error))
    raise
finally:
    client.close()
