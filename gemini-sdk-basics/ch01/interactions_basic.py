# 소스 경로: gemini-sdk-basics/ch01/interactions_basic.py

import os
from typing import cast

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.interactions import Interaction

# .env의 값을 현재 프로세스의 환경 변수로 불러옵니다. 기존 환경 변수는 덮어쓰지 않습니다.
# 경로 없이 load_dotenv()를 호출하면, 일반적으로 해당 파일이 있는 폴더부터 상위 폴더로 올라가며 .env를 찾습니다
load_dotenv()

# GEMINI_API_KEY 환경 변수의 API 키를 사용해 Gemini 클라이언트를 생성합니다.
client = genai.Client(
    # HTTP 통신에 사용할 API 버전, 제한 시간, 재시도 정책을 묶습니다.
    http_options=types.HttpOptions(
        # 요청에 사용할 API 버전을 v1으로 지정합니다.
        api_version="v1",
        # HTTP 요청의 제한 시간입니다. 밀리초 단위이므로 60_000은 60초입니다.
        # Gemini API에 요청을 보낸 후 완성된 응답을 기다리는 시간
        timeout=60_000,
        # 요청이 재시도 대상 오류로 실패했을 때 적용할 정책입니다.
        retry_options=types.HttpRetryOptions(
            # 최초 요청을 포함해 최대 3번 시도합니다. 첫 요청 성공 시 재시도하지 않습니다.
            attempts=3,
            # 첫 재시도 전 대기 시간의 초기값입니다. 단위는 초입니다.
            initial_delay=1.0,
            # 재시도 사이의 대기 시간 상한입니다. 전체 요청 시간의 상한은 아닙니다.
            max_delay=10.0,
            # 재시도를 유발할 HTTP 상태 코드입니다.
            # 408: 요청 시간 초과, 429: 요청 한도 초과
            # 500: 서버 내부 오류, 502: 잘못된 게이트웨이 응답
            # 503: 서비스 이용 불가, 504: 게이트웨이 시간 초과
            http_status_codes=[408, 429, 500, 502, 503, 504],
        ),
    ),
)

try:
    print("Interactions API 호출 시작", flush=True)

    # client.interactions.create()의 반환 타입이 두 가지로 정의되어 있기 때문입니다.
    # Interaction | Stream[InteractionSSEEvent]
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

    # client.interactions.create()의 반환 타입이 두 가지로 정의되어 있기 때문입니다.
    # Interaction | Stream[InteractionSSEEvent]
    # 반환 타입을 검사하는 구성코드를 추가해야 타입검사 오류가 없음
    # 타입 좁히기(Type Narrowing)
    # if not isinstance(interaction, Interaction):
    #     raise TypeError("예상하지 못한 스트리밍 응답입니다.")

    # 또는 cast로 Interaction 타입으로 취급하라고 알려 주는 함수
    # 정적 타입 검사 도구에 해당 타입으로 취급하도록 알려주는 역할
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
