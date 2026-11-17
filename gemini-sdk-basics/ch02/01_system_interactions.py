# 소스 경로: gemini-sdk-basics/ch02/01_system_interactions.py

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.interactions import Interaction

# .env의 설정을 현재 프로세스의 환경 변수로 불러옵니다.
# 이미 설정된 환경 변수는 기본적으로 덮어쓰지 않습니다.
load_dotenv()

# API를 호출하기 전에 필수 설정의 누락이나 빈 값을 확인합니다.
# 여기서는 API 키의 유효성이나 모델 접근 권한까지 검사하지는 않습니다.
if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError(".env 파일에 GEMINI_API_KEY를 설정해 주세요.")
if not os.environ.get("GEMINI_MODEL"):
    raise RuntimeError(".env 파일에 GEMINI_MODEL을 설정해 주세요.")
model = os.environ["GEMINI_MODEL"]

# 모델의 역할과 답변 방식은 system_instruction에, 질문은 input에 지정합니다.
system_instruction = "당신은 Python 입문 강사입니다. 한국어로 짧고 쉽게 답하세요."

# 환경 변수의 API 키를 사용하는 클라이언트를 만듭니다.
# 실제 모델 호출은 아래의 interactions.create()에서 이루어집니다.
client = genai.Client(
    http_options=types.HttpOptions(
        # HTTP 요청 제한 시간은 밀리초 단위이므로 60_000은 60초입니다.
        timeout=60_000,
        retry_options=types.HttpRetryOptions(
            # 재시도 대상 오류가 발생하면 최초 요청을 포함해 최대 3번 시도합니다.
            attempts=3,
            # 재시도 대기 시간은 초 단위입니다.
            initial_delay=1.0,
            # 재시도 사이에는 최대 10초까지 기다립니다. 전체 실행 시간을 제한하는 값은 아닙니다.
            max_delay=10.0,
            # 요청 시간 초과, 호출 한도 초과, 일시적인 서버 오류가 발생하면 다시 요청합니다.
            http_status_codes=[408, 429, 500, 502, 503, 504],
        ),
    ),
)

try:
    prompt = "Python 리스트를 설명해 주세요."
    # 같은 질문을 두 역할에 각각 보내 지침에 따른 응답 차이를 비교합니다.
    # label은 출력용 이름이고, instruction은 모델에 전달할 지침입니다.
    for label, instruction in [
        ("입문 강사", system_instruction + " 일상 비유를 한 가지 사용하세요."),
        (
            "코드 리뷰어",
            "당신은 코드 리뷰어입니다. 한국어로 주의점 두 가지만 답하세요.",
        ),
    ]:
        # 각 호출은 이전 대화 ID를 연결하지 않는 독립적인 요청입니다.
        interaction = client.interactions.create(
            model=model,
            # 이번에 답변받을 사용자 질문입니다. 역할 지침과 구분해서 전달합니다.
            input=prompt,
            # 모델의 역할과 응답 지침은 최상위 매개변수로 전달합니다.
            system_instruction=instruction,
            # 응답이 완성되면 하나의 Interaction 객체로 받습니다.
            stream=False,
            # 후속 대화 연결이나 조회를 위한 서버 저장을 사용하지 않습니다.
            store=False,
        )
        # 반환값이 일반 응답 객체인지 확인한 뒤 응답 내용을 읽습니다.
        # isinstance 검사는 Pylance가 반환 타입을 좁히는 데에도 사용됩니다.
        if not isinstance(interaction, Interaction):
            raise TypeError("일반 Interaction 응답이 필요합니다.")
        # 응답 객체를 받았더라도 생성이 정상 완료됐는지 별도로 확인합니다.
        if interaction.status != "completed":
            raise RuntimeError(f"응답이 완료되지 않았습니다: {interaction.status}")
        print(f"\n[{label}] 사용자 질문: {prompt}")
        print("상태:", interaction.status)
        # output_text로 응답 텍스트를 읽고, 비어 있으면 안내 문구를 출력합니다.
        print(interaction.output_text or "텍스트 응답이 없습니다.")
except Exception as error:
    # try 블록에서 발생한 오류를 출력한 뒤 다시 발생시켜 호출한 쪽에도 오류를 알립니다.
    print("오류:", type(error).__name__, str(error))
    raise
finally:
    # try 블록의 성공 여부와 관계없이 HTTP 연결 자원을 정리합니다.
    client.close()
