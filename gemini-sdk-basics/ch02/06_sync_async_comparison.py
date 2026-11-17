# 소스 경로: gemini-sdk-basics/ch02/06_sync_async_comparison.py
"""5-4. 같은 독립 질문으로 동기 순차 호출과 비동기 동시 호출 비교."""

import asyncio
import os
from time import perf_counter

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.interactions import Interaction

# .env 설정을 환경 변수로 불러오고, 요청 전에 API 키와 모델 이름을 확인합니다.
load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError(".env 파일에 GEMINI_API_KEY를 설정해 주세요.")
if not os.environ.get("GEMINI_MODEL"):
    raise RuntimeError(".env 파일에 GEMINI_MODEL을 설정해 주세요.")
model = os.environ["GEMINI_MODEL"]

# 모델의 역할과 답변 방식은 system_instruction에, 질문은 input에 지정합니다.
system_instruction = "당신은 Python 입문 강사입니다. 한국어로 짧고 쉽게 답하세요."


# 동기 호출과 비동기 호출을 비교하기 위해 같은 질문 목록을 사용합니다.
# 각 질문은 다른 질문의 답변 없이도 독립적으로 답할 수 있습니다.
questions = ["Python 리스트란 무엇인가요?", "Python 튜플이란 무엇인가요?"]


# 독립적인 요청을 동시에 진행하고, 모든 응답을 받은 뒤 결과와 소요 시간을 출력합니다.
async def main():
    # async with 블록 안에서 비동기 클라이언트를 사용하고, 블록을 벗어나면 연결을 닫습니다.
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
        # 클라이언트를 만든 뒤, 모든 질문의 응답을 받는 데 걸리는 시간을 측정합니다.
        start = perf_counter()
        # 서로 독립적인 질문은 동시에 요청할 수 있습니다. 이전 응답 ID가 필요한 대화는 순서대로 요청해야 합니다.
        # *로 질문별 코루틴을 gather에 전달하고, 모든 요청이 끝날 때까지 기다립니다.
        # *(...) 생성된 코루틴을 개별 인자로 펼침 (언패킹)
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
        # 결과 검증과 출력에 드는 시간은 비동기 호출 시간에 포함하지 않습니다.
        elapsed = perf_counter() - start
        # gather는 요청이 끝난 순서와 관계없이 전달받은 순서대로 결과를 반환하므로 질문과 답변을 짝지을 수 있습니다.
        # strict=True는 두 목록의 길이가 다르면 ValueError를 발생시킵니다.
        for question, response in zip(questions, responses, strict=True):
            # 일반 응답 객체인지, 답변이 정상적으로 완료됐는지 확인한 뒤 텍스트를 출력합니다.
            if not isinstance(response, Interaction):
                raise TypeError("일반 Interaction 응답이 필요합니다.")
            if response.status != "completed":
                raise RuntimeError(f"응답이 완료되지 않았습니다: {response.status}")
            print("질문:", question)
            print("응답:", response.output_text)
        print(f"비동기 동시 호출: {elapsed:.2f}초")


if __name__ == "__main__":
    # 먼저 동기 호출을 수행합니다. with를 벗어나면 동기 클라이언트의 연결을 정리합니다.
    with genai.Client(http_options=types.HttpOptions(timeout=60_000)) as client:
        start = perf_counter()
        # 각 요청의 응답 확인과 출력이 끝나야 다음 질문을 요청합니다.
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
        # 동기 측정에는 반복문 안의 응답 검증과 출력 시간도 포함됩니다.
        print(f"동기 순차 호출: {perf_counter() - start:.2f}초")

    # 동기 비교가 끝난 뒤 이벤트 루프를 시작해 비동기 비교를 실행합니다.
    asyncio.run(main())
    # 비동기 호출에만 재시도 설정을 따로 지정했습니다. 재시도가 발생하면 소요 시간에도 영향을 줍니다.
    # 모든 질문에 정상적으로 답변을 받으면 API 호출은 총 4회입니다. 재시도하면 실제 HTTP 요청은 더 많아집니다.
    # 네트워크·서버 상태에 따라 시간과 답변은 달라집니다.
    # 비동기가 항상 빠르다는 보장은 없으며, 이 실습에서는 두 방식의 실행 흐름을 비교합니다.
