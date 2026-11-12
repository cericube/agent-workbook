# 소스 경로: gemini-sdk-basics/02.basic_connection.py
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

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
    # flush=True는 출력 버퍼를 즉시 비워 호출 시작 메시지를 바로 표시합니다.
    print("Gemini API 호출 시작", flush=True)

    # 지정한 모델에 프롬프트와 생성 옵션을 전달합니다.
    # response에는 최초 요청 또는 재시도에서 성공한 응답이 들어갑니다.
    response = client.models.generate_content(
        # 사용할 모델 이름을 환경 변수에서 읽습니다. 변수가 없으면 KeyError가 발생합니다.
        model=os.environ["GEMINI_MODEL"],
        # 모델에 전달할 사용자 요청(프롬프트)입니다.
        contents="Gemini API에 대해서 아주 간단히 한 줄로 소개해 주세요.",
        # 모델의 역할, 응답의 무작위성, 출력 길이 등의 생성 옵션을 묶습니다.
        config={
            # 모델이 응답할 때 따를 역할과 지침을 지정합니다.
            "system_instruction": "당신은 Python 전문 강사입니다.",
            # 토큰 선택의 무작위성을 조절합니다. 낮을수록 비교적 일관된 응답을 유도합니다.
            "temperature": 0.3,
            # 생성할 출력 토큰 수의 상한입니다. 토큰은 글자 수나 단어 수와 다릅니다.
            "max_output_tokens": 500,
        },
    )

    print("Gemini API 호출 완료", flush=True)
    # 응답 텍스트가 없거나 빈 문자열이면 안내 문구를 출력합니다.
    print(response.text or "텍스트 응답이 없습니다.")
    # 실제 응답을 생성한 모델의 버전 정보를 출력합니다.
    print("모델 버전:", response.model_version)

    # 사용량 정보가 포함된 경우에만 토큰 수를 출력합니다.
    usage = response.usage_metadata
    if usage is not None:
        print("입력 토큰:", usage.prompt_token_count)
        print("출력 토큰:", usage.candidates_token_count)
        print("전체 토큰:", usage.total_token_count)

except errors.APIError as e:
    # 재시도 후에도 실패한 경우 등을 포함해 API 오류의 코드와 메시지를 출력합니다.
    print("API 오류:", e.code, e.message)

except Exception as e:
    # API 오류 외의 예외를 처리합니다.
    print("기타 오류:", type(e).__name__, str(e))

finally:
    # try 블록의 성공 여부와 관계없이 클라이언트의 연결 자원을 정리합니다.
    client.close()
