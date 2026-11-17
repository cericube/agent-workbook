# 소스 경로: gemini-sdk-basics/ch01/interactions_basic.py

import os
from typing import cast

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.interactions import Interaction

# .env의 값을 현재 프로세스의 환경 변수로 불러옵니다. 기존 환경 변수는 덮어쓰지 않습니다.
# load_dotenv()에 경로를 지정하지 않으면 일반적으로 현재 파일이 있는 폴더부터 상위 폴더까지 .env를 찾습니다.
load_dotenv()

# GEMINI_API_KEY 환경 변수의 API 키를 사용해 Gemini 클라이언트를 생성합니다.
client = genai.Client(
    # HTTP 요청에 사용할 API 버전과 제한 시간, 재시도 방식을 설정합니다.
    http_options=types.HttpOptions(
        # 요청에 사용할 API 버전을 v1으로 지정합니다.
        api_version="v1",
        # HTTP 요청의 제한 시간입니다. 밀리초 단위이므로 60_000은 60초입니다.
        timeout=60_000,
        # 다시 시도할 오류의 종류와 재시도 횟수, 대기 시간을 설정합니다.
        retry_options=types.HttpRetryOptions(
            # 첫 요청을 포함해 최대 3번 시도합니다. 첫 요청이 성공하면 다시 요청하지 않습니다.
            attempts=3,
            # 첫 재시도까지 기다리는 시간의 기준값이며, 단위는 초입니다.
            initial_delay=1.0,
            # 재시도 사이에는 최대 10초까지 기다립니다. 전체 요청에 걸리는 시간을 제한하는 값은 아닙니다.
            max_delay=10.0,
            # 다음 HTTP 상태 코드로 요청이 실패하면 다시 시도합니다.
            # 408: 요청 시간 초과, 429: 요청 한도 초과
            # 500: 서버 내부 오류, 502: 잘못된 게이트웨이 응답
            # 503: 서비스 이용 불가, 504: 게이트웨이 시간 초과
            http_status_codes=[408, 429, 500, 502, 503, 504],
        ),
    ),
)

try:
    print("Interactions API 호출 시작", flush=True)

    # create()는 stream 설정에 따라 일반 응답 객체나 이벤트 스트림을 반환합니다.
    interaction = client.interactions.create(
        model=os.environ["GEMINI_MODEL"],
        input="Gemini API에 대해서 아지 간단히 한 줄로 소개해 주세요",
        system_instruction="당신은 Python 전문 강사입니다.",
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 500,
        },
        # 스트리밍을 끄고 응답을 하나의 Interaction 객체로 받습니다.
        # True이면 응답 이벤트를 순차적으로 받는 스트리밍 방식이 됩니다.
        stream=False,
        # 후속 대화 연결을 사용하지 않는 단일 요청입니다.
        store=False,
    )

    # isinstance로 반환값을 확인하면 타입 검사 도구도 일반 응답 객체로 판단합니다.
    # if not isinstance(interaction, Interaction):
    #     raise TypeError("예상하지 못한 스트리밍 응답입니다.")

    # 여기서는 cast로 타입 검사 도구에 Interaction 객체임을 알려 줍니다.
    # cast는 실행 중에 객체의 타입을 검사하거나 변환하지 않습니다.
    interaction = cast(Interaction, interaction)

    print("Interactions API 호출 완료", flush=True)
    print("상태:", interaction.status)
    print("Interaction ID:", interaction.id)
    print(interaction.output_text or "텍스트 응답이 없습니다.")

    usage = interaction.usage
    if usage is not None:
        print("입력 토큰:", usage.total_input_tokens)
        print("출력 토큰:", usage.total_output_tokens)
        print("전체 토큰:", usage.total_tokens)

except Exception as error:
    # 실습에서는 오류 종류와 메시지를 확인합니다.
    print("오류:", type(error).__name__, str(error))
finally:
    client.close()
