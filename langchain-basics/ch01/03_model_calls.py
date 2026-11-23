# 파일명: /ch01/03_model_calls.py

import os

from dotenv import load_dotenv
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# .env 파일의 설정을 읽되 이미 설정된 환경 변수는 덮어쓰지 않습니다.
load_dotenv()

# 환경 변수가 없으면 None을 반환하므로 필수 설정을 확인한 뒤 모델을 만듭니다.
model_name = os.getenv("GEMINI_MODEL")
api_key = os.getenv("GEMINI_API_KEY")

if not model_name or not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")

# 같은 모델 객체로 세 가지 호출 방식을 비교합니다.
model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api_key,
    vertexai=False,  # Gemini Developer API 사용
)

# 단순 질문은 문자열로 전달해도 됩니다. 여기서는 사용자 역할을 명시합니다.
# invoke()와 stream()에는 두 질문을 한 요청의 메시지 목록으로 전달합니다.
# batch()에서는 같은 질문들을 각각 독립적인 요청으로 나눕니다.
questions = [
    HumanMessage(content="리스트를 한 문장으로 설명해 줘."),
    HumanMessage(content="튜플을 한 문장으로 설명해 줘."),
]

print("=== invoke(): 완성된 응답 ===")
# 두 질문을 함께 전달하고 완성된 AIMessage 하나를 받습니다.
response = model.invoke(questions)
print(response.text)

print("\n=== stream(): 응답 조각 ===")
# AIMessageChunk를 순서대로 받습니다. 각 조각이 완성된 문장인 것은 아닙니다.
for chunk in model.stream(questions):
    # 줄바꿈 없이 텍스트를 이어 붙이고 출력 버퍼를 비워 바로 표시합니다.
    print(chunk.text, end="", flush=True)

# 조각 출력을 마친 뒤 마지막에 줄을 바꿉니다.
print()

print("\n=== batch(): 독립적인 질문 여러 개 ===")
# batch()의 바깥 목록은 독립적인 요청들, 안쪽 목록은 각 요청의 메시지들입니다.
# list의 불공변성으로 인한 타입 오류를 피하도록 모델 입력 타입을 명시합니다.
inputs: list[LanguageModelInput] = [[question] for question in questions]

# 각 질문을 독립적으로 처리하고 입력 순서에 맞춘 AIMessage 목록을 받습니다.
# 앞 질문의 답변은 다음 질문의 대화 맥락으로 전달되지 않습니다.
responses = model.batch(inputs)
for question, response in zip(questions, responses, strict=True):
    print(question.text)
    print(response.text)
