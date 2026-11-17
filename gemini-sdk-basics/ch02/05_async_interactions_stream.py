# 소스 경로: gemini-sdk-basics/ch02/05_async_interactions_stream.py
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

# .env 설정을 환경 변수로 불러오고, 요청에 필요한 키와 모델 이름이 있는지 확인합니다.
load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError(".env 파일에 GEMINI_API_KEY를 설정해 주세요.")
if not os.environ.get("GEMINI_MODEL"):
    raise RuntimeError(".env 파일에 GEMINI_MODEL을 설정해 주세요.")
model = os.environ["GEMINI_MODEL"]

# 모델의 역할과 답변 방식은 system_instruction에, 질문은 input에 지정합니다.
system_instruction = "당신은 Python 입문 강사입니다. 한국어로 짧고 쉽게 답하세요."


# 비동기 클라이언트로 요청하고, 도착하는 이벤트에서 텍스트와 종료 상태를 확인합니다.
async def main():
    # async with 블록을 벗어나면 비동기 HTTP 연결을 닫습니다.
    async with genai.Client(
        http_options=types.HttpOptions(
            timeout=60_000,  # 요청 제한 시간: 밀리초 단위로 60초
            retry_options=types.HttpRetryOptions(
                # 최초 요청을 포함해 최대 3번 시도합니다.
                attempts=3,
                # 재시도 대기 시간은 초 단위입니다.
                initial_delay=1.0,
                max_delay=10.0,
                # 요청 시간 초과, 호출 한도 초과, 일시적인 서버 오류가 발생하면 다시 요청합니다.
                http_status_codes=[408, 429, 500, 502, 503, 504],
            ),
        ),
    ).aio as client:
        # await로 스트림을 받은 뒤, 아래 async for에서 도착하는 이벤트를 하나씩 읽습니다.
        stream = await client.interactions.create(
            model=model,
            input="Python 리스트의 특징을 세 문장으로 설명해 주세요.",
            system_instruction=system_instruction,
            stream=True,
            store=False,
        )

        # 일반 응답 객체가 반환되면 중단합니다. 이 검사 뒤에는 Pylance도 반환값을 스트림으로 판단합니다.
        if isinstance(stream, Interaction):
            raise TypeError("스트리밍 응답이 필요합니다.")

        # 받은 텍스트 조각을 모아 두었다가 마지막에 하나의 답변으로 이어 붙입니다.
        texts = []
        # 이벤트 수신이 끝나더라도 답변이 정상적으로 완료됐는지는 따로 확인합니다.
        completed = False
        # 다음 이벤트가 도착할 때까지 기다렸다가 순서대로 처리합니다.
        async for event in stream:
            # 새로 받은 텍스트 조각만 모으고 바로 출력해 답변이 조금씩 나타나도록 합니다.
            if isinstance(event, StepDelta) and isinstance(event.delta, TextDelta):
                texts.append(event.delta.text)
                print(event.delta.text, end="", flush=True)
            elif isinstance(event, InteractionCreatedEvent):
                # 생성 이벤트에서 이번 요청의 Interaction ID를 읽어 출력합니다.
                print("Interaction ID:", event.interaction.id, flush=True)
            elif isinstance(event, InteractionCompletedEvent):
                # 완료 이벤트를 받았더라도 상태가 completed인 경우에만 정상 완료로 봅니다.
                completed = event.interaction.status == "completed"
                print("\n종료 상태:", event.interaction.status)
            elif isinstance(event, ErrorEvent):
                # 오류 이벤트를 받으면 예외를 발생시킵니다. async with 블록을 벗어나면서 연결도 닫습니다.
                raise RuntimeError(f"스트리밍 오류: {event.error}")
            # 단계 시작·종료나 상태 변경을 알리는 나머지 이벤트는 출력하지 않습니다.
        # 완료 상태를 확인하지 못한 채 스트림이 끝나면 예외를 발생시킵니다.
        if not completed:
            raise RuntimeError("완료 이벤트 없이 스트림이 끝났습니다.")
        print("조합한 응답:", "".join(texts) or "텍스트 응답이 없습니다.")


if __name__ == "__main__":
    # 직접 실행할 때 이벤트 루프를 시작하고 main()이 끝날 때까지 기다립니다.
    asyncio.run(main())
