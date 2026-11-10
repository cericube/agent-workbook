import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# 현재 Python 파일과 같은 디렉터리의 .env 파일에서 환경 변수를 불러옵니다.
load_dotenv(Path(__file__).parent / ".env")
print(Path(__file__).parent)

# 환경 변수에서 Gemini API 인증 키와 호출할 모델 이름을 읽습니다.
api_key = os.getenv("GEMINI_API_KEY")
model_name = str(os.getenv("GEMINI_MODEL"))

# 인증 키 자체를 노출하지 않고, 로드 여부와 모델 이름만 출력합니다.
# flush=True는 출력 버퍼를 즉시 비워 진행 상황을 바로 확인하게 합니다.
print("API Key 로드:", bool(api_key), flush=True)
print("모델 이름: ", model_name, flush=True)

# 인증 키가 없으면 API를 호출하기 전에 실행을 중단합니다.
if not api_key:
    raise RuntimeError("GEMINI_API_KEY가 없습니다.")

print("Client 생성 시작", flush=True)

# 인증 정보와 HTTP 요청 옵션을 지정해 Gemini 클라이언트를 생성합니다.
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=10000,  # 요청 제한 시간: 밀리초 단위로 10초
        retry_options=types.HttpRetryOptions(
            attempts=1
        ),  # 최초 요청을 포함해 한 번만 시도
    ),
)

print("Client 생성 완료", flush=True)

try:
    print("Gemini API 호출 시작", flush=True)

    # 지정한 모델에 프롬프트를 보내 텍스트 응답을 생성합니다.
    response = client.models.generate_content(
        model=model_name,
        contents="Gemini API에 대해서 아주 간단히 한줄로 소개해 주세요.",
    )

    print("Gemini API 호출 완료", flush=True)
    print(response.text)  # 응답 객체에서 생성된 텍스트를 출력합니다.

except Exception as e:
    # API 호출 또는 응답 처리 중 발생한 예외의 종류와 내용을 출력합니다.
    print("오류 유형:", type(e).__name__, flush=True)
    print("오류 내용:", str(e), flush=True)

finally:
    # 성공 여부와 관계없이 클라이언트가 사용하는 연결 등의 자원을 정리합니다.
    client.close()
