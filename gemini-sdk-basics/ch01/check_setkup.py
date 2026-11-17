# 소스 경로: gemini-sdk-basics/ch01/check_setkup.py
import os
from importlib.metadata import version

from dotenv import load_dotenv
from google import genai

# .env의 값을 현재 Python 프로세스의 환경 변수로 불러옵니다.
# 시스템 설정을 영구적으로 바꾸지는 않으며, 기존 환경 변수는 기본적으로 덮어쓰지 않습니다.
# load_dotenv()에 경로를 지정하지 않으면 일반적으로 현재 파일이 있는 폴더부터 상위 폴더까지 .env를 찾습니다.
load_dotenv()

# 환경 변수가 없으면 KeyError가 발생합니다.
# model = os.environ["GEMINI_MODEL"]
# 환경 변수가 없으면 None을 반환합니다.
# model = os.getenv("GEMINI_MODEL")
# 환경 변수가 없으면 지정한 기본값을 사용합니다.
# model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# os.environ.get()은 환경 변수의 문자열 값을 읽으며, 변수가 없으면 None을 반환합니다.
model = os.environ.get("GEMINI_MODEL")

# API 키나 모델 이름이 없거나 빈 문자열이면 오류를 발생시켜 실행을 중단합니다.
# 여기서는 값의 존재만 확인하며, API 키의 유효성이나 해당 모델을 사용할 수 있는지는 확인하지 않습니다.
if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError(".env 파일에 GEMINI_API_KEY를 설정해 주세요.")
if not os.environ.get("GEMINI_MODEL"):
    raise RuntimeError("GEMINI_MODEL 환경 변수를 설정해 주세요.")


# 설치된 SDK의 버전과 설정된 모델 이름을 출력합니다. API 키는 출력하지 않습니다.
print("SDK 버전:", version("google-genai"))
print("모델:", os.environ["GEMINI_MODEL"])
# Client가 호출 가능한 객체인지 확인합니다. 클라이언트를 생성하거나 API를 호출하지는 않습니다.
print("클라이언트 사용 준비:", callable(genai.Client))
