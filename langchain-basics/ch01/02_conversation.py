# 파일명: /ch01/02_conversation.py

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# .env 파일을 찾아 설정을 환경 변수로 불러옵니다.
# 이미 설정된 환경 변수는 덮어쓰지 않으므로 실행 환경의 설정이 우선합니다.
load_dotenv()

# 사용할 Gemini 모델 이름과 인증용 API 키를 읽습니다.
# 해당 환경 변수가 없으면 os.getenv()는 None을 반환합니다.
model_name = os.getenv("GEMINI_MODEL")
api_key = os.getenv("GEMINI_API_KEY")

# 필수 설정이 없거나 빈 문자열이면 안내 메시지와 함께 종료합니다.
if not model_name or not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")

# Gemini를 LangChain의 채팅 모델 인터페이스로 호출할 수 있도록 모델 객체를 만듭니다.
model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api_key,
    vertexai=False,  # Gemini Developer API 사용
)

# SystemMessage에는 답변 방식에 대한 지침을, HumanMessage에는 사용자 질문을 담습니다.
# 목록의 순서대로 메시지를 전달해 대화의 맥락을 구성합니다.
messages = [
    SystemMessage(
        content="파이썬 입문자에게 한국어로 한 문장으로 간결하게 설명해 주세요."
    ),
    HumanMessage(content="리스트와 튜플 차이는?."),
]

# 메시지 목록을 전송하고 응답을 기다린 뒤 AIMessage 객체를 받습니다.
first_reply = model.invoke(messages)
print("첫 번째 답변")
# text 속성으로 응답 메시지의 텍스트 내용만 추출해 출력합니다.
print(first_reply.text)

# 모델의 답변과 후속 질문을 순서대로 추가해 앞선 대화 내용을 보존합니다.
messages.append(first_reply)
messages.append(
    HumanMessage(content="그 차이를 보여주는 짧은 snippet 코드 예시 만들어 줘.")
)

# 이전 질문과 답변을 포함한 전체 이력을 다시 전송합니다.
# 이 예제에서는 messages 목록을 직접 관리해 후속 질문의 맥락을 전달합니다.
second_reply = model.invoke(messages)
print("\n")
print("두 번째 답변")
print(second_reply.text)
