"""5-4. 같은 독립 질문으로 동기 순차 호출과 비동기 동시 호출 비교."""

import asyncio
import os
from time import perf_counter

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


questions = ["Python 리스트란 무엇인가요?", "Python 튜플이란 무엇인가요?"]


async def main():
    async with genai.Client(
        http_options=types.HttpOptions(timeout=60_000)
    ).aio as client:
        start = perf_counter()
        # 서로 독립적인 질문만 함께 실행합니다. 이전 ID가 필요한 대화는 순차 호출합니다.
        responses = await asyncio.gather(
            *(
                client.interactions.create(
                    model=model,
                    input=question,
                    system_instruction=system_instruction,
                    stream=False,
                    store=False,
                )
                for question in questions
            )
        )
        elapsed = perf_counter() - start
        for question, response in zip(questions, responses, strict=True):
            if not isinstance(response, Interaction):
                raise TypeError("일반 Interaction 응답이 필요합니다.")
            if response.status != "completed":
                raise RuntimeError(f"응답이 완료되지 않았습니다: {response.status}")
            print("질문:", question)
            print("응답:", response.output_text)
        print(f"비동기 동시 호출: {elapsed:.2f}초")


if __name__ == "__main__":
    with genai.Client(http_options=types.HttpOptions(timeout=60_000)) as client:
        start = perf_counter()
        for question in questions:
            response = client.interactions.create(
                model=model,
                input=question,
                system_instruction=system_instruction,
                stream=False,
                store=False,
            )
            if not isinstance(response, Interaction):
                raise TypeError("일반 Interaction 응답이 필요합니다.")
            if response.status != "completed":
                raise RuntimeError(f"응답이 완료되지 않았습니다: {response.status}")
            print("질문:", question)
            print("응답:", response.output_text)
        print(f"동기 순차 호출: {perf_counter() - start:.2f}초")

    asyncio.run(main())
    # 총 4번 요청합니다. 네트워크·서버 상태에 따라 시간과 답변은 달라집니다.
    # 비동기가 항상 빠르다는 보장은 없으며, 이 실습은 실행 구조를 비교합니다.
