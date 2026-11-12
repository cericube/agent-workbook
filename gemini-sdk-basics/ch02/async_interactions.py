"""5-2. Interactions API 비동기 호출과 순차 대화 연결."""

import asyncio
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


async def main():
    # async with가 비동기 HTTP 연결을 정리합니다.
    async with genai.Client(
        http_options=types.HttpOptions(timeout=60_000)
    ).aio as client:
        previous_id = None
        for question in [
            "저는 민수이고 리스트를 공부합니다.",
            "제 이름과 공부 주제를 알려 주세요.",
        ]:
            # 첫 요청은 이전 ID 없이, 후속 요청은 직전 ID를 지정합니다.
            # System Instruction은 매 요청에 다시 전달합니다.
            if previous_id is None:
                interaction = await client.interactions.create(
                    model=model,
                    input=question,
                    system_instruction=system_instruction,
                    store=True,
                    stream=False,
                )
            else:
                interaction = await client.interactions.create(
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
            previous_id = interaction.id
            print("ID:", previous_id)
            print(interaction.output_text or "텍스트 응답이 없습니다.")


if __name__ == "__main__":
    asyncio.run(main())
