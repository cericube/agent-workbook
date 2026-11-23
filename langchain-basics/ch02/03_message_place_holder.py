# 파일명: /ch02/03_message_place_holder.py

import os

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

# .env 파일의 설정을 읽되 이미 설정된 환경 변수는 덮어쓰지 않습니다.
load_dotenv()

# 사용할 모델 이름과 API 키를 읽습니다. 환경 변수가 없으면 None을 반환합니다.
model_name = os.getenv("GEMINI_MODEL")
api_key = os.getenv("GEMINI_API_KEY")

# 필수 설정이 없거나 빈 문자열이면 모델을 만들기 전에 종료합니다.
if not model_name or not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")


# 대화 이력을 포함한 메시지 목록을 Gemini에 전달할 모델 객체를 만듭니다.
model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api_key,
    vertexai=False,  # Gemini Developer API 사용
)

# 첫 질문에 포함할 요약 대상 문서입니다.
document = (
    "파이썬의 리스트와 튜플은 여러 값을 순서대로 저장합니다. "
    "리스트는 생성한 뒤에도 요소를 추가하거나 수정할 수 있습니다. "
    "튜플은 생성한 뒤 요소를 다른 값으로 바꿀 수 없습니다. "
    "내용을 자주 바꾸는 데이터에는 리스트를, "
    "요소 구성을 유지할 데이터에는 튜플을 사용할 수 있습니다."
)


# 시스템 지침, 이전 대화, 새 사용자 질문 순서로 메시지를 구성합니다.
# MessagesPlaceholder는 history의 메시지들을 역할과 순서를 유지한 채 삽입합니다.
template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "제공된 문서를 바탕으로 입문자가 이해할 수 있도록 한국어로 답하세요.",
        ),
        MessagesPlaceholder("history"),
        ("human", "{question}"),
    ]
)

# 첫 요청에는 이전 대화가 없으므로 빈 목록을 전달합니다.
# BaseMessage로 타입을 지정해 사용자 메시지와 모델 응답을 함께 저장합니다.
previous_messages: list[BaseMessage] = []

# format_messages()는 변수를 채운 메시지 목록을 만들며 모델을 호출하지 않습니다.
first_message = template.format_messages(
    history=previous_messages,
    question=f"다음 문서를 두 문장으로 요약해 주세요.\n문서:\n{document}",
)

# 실제 전송할 메시지의 역할과 내용을 확인합니다.
print("=== 첫 요청 메시지 ===")
for message in first_message:
    print(f"[{type(message).__name__}]\n{message.text}\n")

# 완성된 메시지 목록을 전송하고 AIMessage 응답을 받습니다.
first_reply = model.invoke(first_message)
print("=== 첫 요약 답변 ===")
print(first_reply.text)
# 마지막 메시지인 첫 사용자 질문과 모델 응답을 대화 이력에 차례로 추가합니다.
# 시스템 지침은 템플릿에서 매번 추가하므로 이력에는 중복 저장하지 않습니다.
previous_messages.extend([first_message[-1], first_reply])

print("=== 히스토리 ===")
for message in previous_messages:
    print(f"[{type(message).__name__}]\n{message.text}\n")

# 앞서 저장한 질문과 답변을 history에 삽입한 뒤 후속 질문을 덧붙입니다.
# MessagesPlaceholder가 이력을 자동 저장하는 것은 아니므로 목록을 직접 관리합니다.
follow_up_messages = template.format_messages(
    history=previous_messages,
    question="그 내용을 예시로 설명해 줘.",
)

print("=== 후속 요청 메시지 ===")
for message in follow_up_messages:
    print(f"[{type(message).__name__}]\n{message.text}\n")

# 이전 문서와 요약 답변이 함께 전달되어 후속 질문에서 앞선 내용을 참조할 수 있습니다.
response = model.invoke(follow_up_messages)
print("=== 후속 답변 ===")
print(response.text)
