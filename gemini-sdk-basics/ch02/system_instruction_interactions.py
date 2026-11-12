"""1. Interactions API의 system_instruction."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.interactions import Interaction

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
    prompt = "Python 리스트를 설명해 주세요."
    # 사용자 질문은 유지하고 System Instruction의 역할과 응답 방식을 바꿉니다.
    for label, instruction in [
        ("입문 강사", system_instruction + " 일상 비유를 한 가지 사용하세요."),
        (
            "코드 리뷰어",
            "당신은 코드 리뷰어입니다. 한국어로 주의점 두 가지만 답하세요.",
        ),
    ]:
        interaction = client.interactions.create(
            model=model,
            input=prompt,
            # 모델의 역할과 응답 지침은 최상위 매개변수로 전달합니다.
            system_instruction=instruction,
            stream=False,
            store=False,
        )
        if not isinstance(interaction, Interaction):
            raise TypeError("일반 Interaction 응답이 필요합니다.")
        if interaction.status != "completed":
            raise RuntimeError(f"응답이 완료되지 않았습니다: {interaction.status}")
        print(f"\n[{label}] 사용자 질문: {prompt}")
        print("상태:", interaction.status)
        print(interaction.output_text or "텍스트 응답이 없습니다.")
except Exception as error:
    print("오류:", type(error).__name__, str(error))
    raise
finally:
    client.close()
