# 소스 경로: gemini-sdk-basics/ch02/04_async_interactions.py
"""5-2. Interactions API 비동기 호출과 순차 대화 연결."""

import asyncio
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.interactions import Interaction

# .env 파일을 읽어 환경 변수를 설정합니다. 이미 설정된 값은 그대로 사용합니다.
load_dotenv()

# API 키나 모델 이름이 비어 있으면 요청을 보내기 전에 실행을 중단합니다.
if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError(".env 파일에 GEMINI_API_KEY를 설정해 주세요.")
if not os.environ.get("GEMINI_MODEL"):
    raise RuntimeError(".env 파일에 GEMINI_MODEL을 설정해 주세요.")
model = os.environ["GEMINI_MODEL"]

# 모델의 역할과 답변 방식은 system_instruction에, 질문은 input에 지정합니다.
system_instruction = "당신은 Python 입문 강사입니다. 한국어로 짧고 쉽게 답하세요."


# async def로 정의한 함수는 호출하면 코루틴 객체를 반환합니다.
# 아래의 asyncio.run()이 이 코루틴을 실행합니다.
async def main():
    # .aio는 비동기 호출에 사용합니다.
    # async with 블록을 벗어나면 오류가 발생한 경우에도 비동기 HTTP 연결을 닫습니다.
    async with genai.Client(
        http_options=types.HttpOptions(
            # 요청 제한 시간입니다. 밀리초 단위이므로 60_000은 60초입니다.
            timeout=60_000,
            retry_options=types.HttpRetryOptions(
                # 아래에 지정한 HTTP 오류가 발생하면 첫 요청을 포함해 최대 3번 시도합니다.
                attempts=3,
                # 재시도 대기 시간은 초 단위이며, 초기값은 1초입니다.
                initial_delay=1.0,
                # 재시도 사이에 기다리는 시간은 최대 10초입니다.
                max_delay=10.0,
                # 요청 시간 초과, 호출 한도 초과, 일시적인 서버 오류가 나면 다시 요청합니다.
                http_status_codes=[408, 429, 500, 502, 503, 504],
            ),
        ),
    ).aio as client:
        # 첫 질문은 연결할 이전 응답이 없으므로 새 대화로 시작합니다.
        previous_id = None
        # 다음 질문에는 앞선 응답 ID가 필요하므로 두 요청을 순서대로 보냅니다.
        # 비동기 호출을 사용하더라도 이 반복문에서 여러 질문을 동시에 보내지는 않습니다.
        for question in [
            "저는 민수이고 리스트를 공부합니다.",
            "제 이름과 공부 주제를 알려 주세요.",
        ]:
            # 첫 요청에는 이전 응답 ID를 넣지 않고, 다음 요청부터 직전 응답 ID를 전달합니다.
            # 이전 응답 ID로 지침까지 전달되지는 않으므로 system_instruction은 요청할 때마다 보냅니다.
            if previous_id is None:
                # await로 요청을 보내고 응답을 기다린 뒤 아래 코드를 실행합니다.
                # 기다리는 동안 이벤트 루프는 다른 코루틴이 있다면 실행할 수 있습니다.
                interaction = await client.interactions.create(
                    model=model,
                    input=question,
                    system_instruction=system_instruction,
                    # 입력과 응답을 서버에 저장해 다음 질문에서 ID로 연결할 수 있게 합니다.
                    store=True,
                    # 비동기로 호출하되, 결과는 스트림이 아닌 완성된 응답 객체로 받습니다.
                    stream=False,
                )
            else:
                interaction = await client.interactions.create(
                    model=model,
                    input=question,
                    system_instruction=system_instruction,
                    store=True,
                    stream=False,
                    # 서버에 저장된 이전 대화를 바탕으로 이번 질문에 답하도록 연결합니다.
                    previous_interaction_id=previous_id,
                )
            # 일반 응답 객체인지 확인합니다. Pylance도 이 검사로 객체의 타입을 판단합니다.
            if not isinstance(interaction, Interaction):
                raise TypeError("일반 Interaction 응답이 필요합니다.")
            # 답변이 정상 완료됐고 ID가 있어야 다음 질문을 이어 갈 수 있습니다.
            # 조건을 만족하지 못하면 예외가 발생해 다음 질문은 보내지 않습니다.
            if interaction.status != "completed" or not interaction.id:
                raise RuntimeError(f"대화가 완료되지 않았습니다: {interaction.status}")
            # 다음 질문이 방금 받은 응답에서 이어지도록 최신 ID를 보관합니다.
            previous_id = interaction.id
            print("ID:", previous_id)
            # 답변 텍스트가 비어 있으면 안내 문구를 출력합니다.
            print(interaction.output_text or "텍스트 응답이 없습니다.")

    # 연결을 닫아도 store=True로 저장한 서버 기록이 삭제되지는 않습니다.


# 이 파일을 직접 실행할 때만 비동기 실습을 시작합니다.
if __name__ == "__main__":
    # 이벤트 루프를 만들어 main()을 실행하고, 끝나면 루프를 닫습니다.
    asyncio.run(main())
