import os

from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model_name = os.getenv("GEMINI_MODEL")
api_key = os.getenv("GEMINI_API_KEY")

if not model_name or not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")

model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api_key,
    vertexai=False,  # Gemini Developer API 사용
)

document = (
    "파이썬의 리스트와 튜플은 여러 값을 순서대로 저장합니다. "
    "리스트는 생성한 뒤에도 요소를 추가하거나 수정할 수 있습니다. "
    "튜플은 생성한 뒤 요소를 다른 값으로 바꿀 수 없습니다. "
    "내용을 자주 바꾸는 데이터에는 리스트를, "
    "요소 구성을 유지할 데이터에는 튜플을 사용할 수 있습니다."
)

chat_template = ChatPromptTemplate(
    [
        ("system", "문서의 핵심 내용을 {language}로 두 문장으로 요약하세요."),
        ("human", "문서:\n{document}"),
    ]
)

messages = chat_template.format_messages(language="한국어", document=document)

print("=== 모델에 보낼 메시지 ===")
for message in messages:
    print(f"[{type(message).__name__}]\n{message.text}\n")


response = model.invoke(messages)
print("=== 요약 답변 ===")
print(response.text)


print(" ===  메시지별 Template 객체 만들")

system_template = SystemMessagePromptTemplate.from_template(
    "문서의 핵심 내용을 {language}로 두 문장으로 요약하세요."
)
human_template = HumanMessagePromptTemplate.from_template("문서:\n{document}")

chat_template = ChatPromptTemplate.from_messages(
    [
        system_template,
        human_template,
    ]
)
messages = chat_template.format_messages(language="한국어", document=document)
for message in messages:
    print(f"[{type(message).__name__}]\n{message.text}\n")
