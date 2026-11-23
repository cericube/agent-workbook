# 파일명: /ch01/01_hello.py

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# .env 파일을 찾아 설정을 환경 변수로 불러옵니다.
# 이미 설정된 환경 변수는 덮어쓰지 않으므로 실행 환경의 설정이 우선합니다.
load_dotenv()

# 사용할 Gemini 모델 이름과 인증용 API 키를 읽습니다.
# os.getenv()는 해당 환경 변수가 없으면 None을 반환합니다.
model_name = os.getenv("GEMINI_MODEL")
api_key = os.getenv("GEMINI_API_KEY")

# 필수 설정이 없거나 빈 문자열이면 모델을 생성하기 전에 안내 메시지와 함께 종료합니다.
if not model_name or not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")

# Gemini를 LangChain의 채팅 모델 인터페이스로 호출할 수 있도록 모델 객체를 만듭니다.
# Gemini는 Gemini Developer API와 Google Cloud의 (구)Vertex AI 경로를 통해 호출할 수 있습니다
model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api_key,
    vertexai=False,  # Gemini Developer API 사용
)

# invoke()는 프롬프트를 전송하고 응답을 기다린 뒤 AIMessage 객체를 반환합니다.
response = model.invoke("LangChaing을 한국어로 한 문장으로 설명해 줘.")
# 응답이 문자열이 아닌 메시지 객체임을 타입으로 확인합니다.
print(type(response))
# text 속성으로 메시지의 텍스트 내용만 추출해 출력합니다.
print(response.text)
