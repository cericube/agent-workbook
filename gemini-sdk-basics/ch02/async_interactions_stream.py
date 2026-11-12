"""5-3. Interactions API 비동기 스트리밍 이벤트 처리."""

import asyncio
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.interactions import (
    ErrorEvent,
    Interaction,
    InteractionCompletedEvent,
    InteractionCreatedEvent,
    StepDelta,
    TextDelta,
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


async def main():
    # async with가 비동기 HTTP 연결을 정리합니다.
    async with genai.Client(
        http_options=types.HttpOptions(timeout=60_000)
    ).aio as client:
        stream = await client.interactions.create(
            model=model,
            input="Python 리스트의 특징을 세 문장으로 설명해 주세요.",
            system_instruction=system_instruction,
            stream=True,
            store=False,
        )

        # 일반 응답 타입을 제외해 스트림으로 타입을 좁힙니다.
        if isinstance(stream, Interaction):
            raise TypeError("스트리밍 응답이 필요합니다.")

        texts = []
        completed = False
        async for event in stream:
            # google-genai 3.0.0의 텍스트 조각 이벤트입니다.
            if isinstance(event, StepDelta) and isinstance(event.delta, TextDelta):
                texts.append(event.delta.text)
                print(event.delta.text, end="", flush=True)
            elif isinstance(event, InteractionCreatedEvent):
                print("Interaction ID:", event.interaction.id, flush=True)
            elif isinstance(event, InteractionCompletedEvent):
                completed = event.interaction.status == "completed"
                print("\n종료 상태:", event.interaction.status)
            elif isinstance(event, ErrorEvent):
                raise RuntimeError(f"스트리밍 오류: {event.error}")
            # step.start, step.stop, 상태 갱신 등은 텍스트로 출력하지 않습니다.
        if not completed:
            raise RuntimeError("완료 이벤트 없이 스트림이 끝났습니다.")
        print("조합한 응답:", "".join(texts) or "텍스트 응답이 없습니다.")


if __name__ == "__main__":
    asyncio.run(main())
