# 소스 경로: gemini-sdk-basics/ch02/03_interactions_stream.py
"""4. Interactions API의 스트리밍 이벤트 처리."""

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

# .env 파일을 읽어 환경 변수를 설정합니다. 이미 설정된 값은 그대로 사용합니다.
load_dotenv()

# API 키와 모델 이름이 비어 있으면 실행을 중단합니다.
# 키가 유효한지, 해당 모델을 사용할 수 있는지는 실제 요청을 보낼 때 확인됩니다.
if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError(".env 파일에 GEMINI_API_KEY를 설정해 주세요.")
if not os.environ.get("GEMINI_MODEL"):
    raise RuntimeError(".env 파일에 GEMINI_MODEL을 설정해 주세요.")
model = os.environ["GEMINI_MODEL"]

# 모델의 역할과 답변 방식은 system_instruction에, 질문은 input에 지정합니다.
system_instruction = "당신은 Python 입문 강사입니다. 한국어로 짧고 쉽게 답하세요."


# 환경 변수에 설정한 API 키로 클라이언트를 만들고, 제한 시간과 재시도 방식을 정합니다.
client = genai.Client(
    http_options=types.HttpOptions(
        # 요청 제한 시간입니다. 밀리초 단위이므로 60_000은 60초입니다.
        timeout=60_000,
        retry_options=types.HttpRetryOptions(
            # 아래에 지정한 HTTP 오류가 발생하면 첫 요청을 포함해 최대 3번 시도합니다.
            attempts=3,
            # 첫 재시도 전에는 1초를 기다립니다.
            initial_delay=1.0,
            # 재시도 사이에 기다리는 시간은 최대 10초입니다. 전체 실행 시간을 뜻하지는 않습니다.
            max_delay=10.0,
            # 요청 시간 초과, 호출 한도 초과, 일시적인 서버 오류가 발생했을 때 다시 요청합니다.
            http_status_codes=[408, 429, 500, 502, 503, 504],
        ),
    ),
)
try:
    prompt = "Python 리스트의 특징을 세 문장으로 설명해 주세요."
    # API 응답을 기다리기 전에 안내 문구가 보이도록 바로 출력합니다.
    print("[일반 응답: 완성될 때까지 기다립니다.]", flush=True)
    interaction = client.interactions.create(
        model=model,
        input=prompt,
        system_instruction=system_instruction,
        # 답변이 완성되면 Interaction 객체 하나로 받습니다.
        stream=False,
        # 나중에 조회하거나 대화를 이어 갈 필요가 없으므로 서버에 저장하지 않습니다.
        store=False,
    )
    # 반환값이 일반 응답 객체인지 확인합니다. Pylance도 이 검사로 객체의 타입을 판단합니다.
    if not isinstance(interaction, Interaction):
        raise TypeError("일반 Interaction 응답이 필요합니다.")
    # 응답을 받았더라도 답변이 끝까지 생성됐는지 확인해야 합니다.
    if interaction.status != "completed":
        raise RuntimeError(f"응답이 완료되지 않았습니다: {interaction.status}")
    print(interaction.output_text or "텍스트 응답이 없습니다.")

    # 같은 질문을 다시 보내 일반 응답과 스트리밍이 화면에 어떻게 출력되는지 비교합니다.
    # 두 번 따로 요청하므로 답변 내용은 달라질 수 있습니다. 스트리밍이 항상 더 빠른 것도 아닙니다.
    print("\n[스트리밍: 도착하는 조각부터 출력합니다.]", flush=True)
    stream = client.interactions.create(
        model=model,
        input=prompt,
        system_instruction=system_instruction,
        # 요청이 시작되고 답변이 생성되는 동안, 진행 상황과 텍스트를 이벤트로 받습니다.
        stream=True,
        store=False,
    )

    # 일반 응답 객체가 반환됐다면 중단합니다. 이 검사 뒤에는 Pylance도 스트림으로 판단합니다.
    if isinstance(stream, Interaction):
        raise TypeError("스트리밍 응답이 필요합니다.")

    # 받은 텍스트를 목록에 모아 두었다가 마지막에 하나의 답변으로 이어 붙입니다.
    texts = []
    # 이벤트 수신이 끝나더라도 답변이 정상 완료됐는지는 따로 확인합니다.
    completed = False
    # 이벤트가 도착할 때마다 종류에 따라 텍스트를 출력하거나 상태를 확인합니다.
    for event in stream:
        # StepDelta에는 새로 생성된 데이터가 담깁니다. 그중 답변 텍스트인 TextDelta만 출력합니다.
        # 한 번에 받는 텍스트의 길이는 매번 다를 수 있으며, 반드시 토큰 하나씩 오는 것은 아닙니다.
        if isinstance(event, StepDelta) and isinstance(event.delta, TextDelta):
            texts.append(event.delta.text)
            # 줄을 바꾸지 않고 바로 출력해 답변이 조금씩 나타나도록 합니다.
            print(event.delta.text, end="", flush=True)
        # Interaction이 만들어지면 ID를 출력합니다. 이때는 아직 답변을 생성하는 중입니다.
        elif isinstance(event, InteractionCreatedEvent):
            print("Interaction ID:", event.interaction.id, flush=True)
        # 종료 이벤트를 받으면 상태를 확인합니다. completed일 때만 정상 완료로 기록합니다.
        elif isinstance(event, InteractionCompletedEvent):
            completed = event.interaction.status == "completed"
            print("\n종료 상태:", event.interaction.status)
        # 서버에서 오류 이벤트가 오면 예외를 발생시켜 응답 처리를 중단합니다.
        elif isinstance(event, ErrorEvent):
            raise RuntimeError(f"스트리밍 오류: {event.error}")
        # 단계 시작·종료나 상태 변경을 알리는 나머지 이벤트는 출력하지 않습니다.
    # 답변 일부를 받았더라도 정상 완료를 확인하지 못했다면 오류로 처리합니다.
    if not completed:
        raise RuntimeError("완료 이벤트 없이 스트림이 끝났습니다.")
    # 지금까지 받은 텍스트를 순서대로, 사이에 공백을 넣지 않고 이어 붙입니다.
    print("조합한 응답:", "".join(texts) or "텍스트 응답이 없습니다.")
except Exception as error:
    # 요청을 보내거나 이벤트를 받다가 오류가 나면 내용을 출력하고 예외를 다시 발생시킵니다.
    print("오류:", type(error).__name__, str(error))
    raise
finally:
    # 오류가 발생해도 사용한 HTTP 연결은 닫습니다.
    client.close()
