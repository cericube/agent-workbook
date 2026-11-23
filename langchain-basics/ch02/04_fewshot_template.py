# 파일명: /ch02/04_fewshot_template.py

import os

from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    FewShotPromptTemplate,
    PromptTemplate,
)
from langchain_google_genai import ChatGoogleGenerativeAI

# .env 파일의 설정을 읽되 이미 설정된 환경 변수는 덮어쓰지 않습니다.
load_dotenv()

# 사용할 모델 이름과 API 키를 읽고, 누락되거나 빈 문자열이면 종료합니다.
model_name = os.getenv("GEMINI_MODEL")
api_key = os.getenv("GEMINI_API_KEY")

if not model_name or not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")

# 완성된 프롬프트를 Gemini Developer API로 전송할 모델 객체를 만듭니다.
model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api_key,
    vertexai=False,  # Gemini Developer API 사용
)


# 시스템 지침으로 분류 범위와 답변 형식을 지정합니다.
instruction = "고객 문의를 배송, 환불, 계정 중 하나로 분류하세요. 분류명만 답하세요."
# few-shot 예시로 문의와 정답을 함께 제공해 분류 기준을 보여줍니다.
# 모델을 별도로 학습시키는 대신 요청 메시지에 예시를 포함합니다.
examples = [
    {"inquiry": "주문한 상품이 아직 도착하지 않았어요.", "category": "배송"},
    {"inquiry": "결제를 취소하고 돈을 돌려받고 싶어요.", "category": "환불"},
    {"inquiry": "비밀번호를 잊어버려 로그인할 수 없어요.", "category": "계정"},
]
# 정답을 제공하지 않고 모델이 분류하도록 할 새 문의입니다.
new_inquiry = "택배가 지금 어디에 있는지 알고 싶어요."

# 예시 하나를 사용자 문의와 모델 답변 역할의 메시지 쌍으로 만듭니다.
example_template = ChatPromptTemplate.from_messages(
    [
        ("human", "문의:{inquiry}"),
        ("ai", "{category}"),
    ]
)

# examples의 각 데이터를 example_prompt에 넣어 문의와 답변으로 이루어진 예시 메시지를 만듭니다.
few_shot_template = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_template,
)

# 시스템 지침, 예시 메시지들, 새 문의 순서로 하나의 요청을 구성합니다.
chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", instruction),
        few_shot_template,
        # 히스토리 위치
        ("human", "문의: {inquiry}"),
    ]
)

# 새 문의를 채워 메시지 목록을 만듭니다. 이 단계에서는 모델을 호출하지 않습니다.
# 예시의 inquiry는 examples에서, 마지막 사용자 메시지의 inquiry는 이 인자에서 가져옵니다.
messages = chat_template.format_messages(inquiry=new_inquiry)

# 실제 전송할 메시지의 역할과 내용을 확인합니다.
print("=== 채팅 메시지 입력 ===")
for message in messages:
    print(f"[{type(message).__name__}]\n{message.text}\n")

# 예시를 포함한 전체 목록을 한 번에 전송하고 새 문의에 대한 응답을 받습니다.
chat_response = model.invoke(messages)
print("=== 채팅 방식의 분류 ===")
print(chat_response.text)

###################################################
print("######################### PromptTemplate 방식 #########################")
example_template = PromptTemplate.from_template("문의: {inquiry}\n분류: {category}")
text_template = FewShotPromptTemplate(
    examples=examples,  # 프롬프트에 넣을 예시 데이터
    example_prompt=example_template,  # 예시 한 건을 문자열로 바꾸는 서식
    prefix=instruction,  # 예시 앞에 붙이는 문장, 분류명만 답하라고 지시문
    suffix="문의: {inquiry}\n분류:",  # 예시 뒤에 붙이는 서식, {inquiry}에 새 문의를 넣고 분류:에서 끝냅니다.
    input_variables=[
        "inquiry"
    ],  # 최종 프롬프트가 호출 시 받는 입력 변수(inquiry=new_inquiry)
    example_separator="\n\n",  # 각 블록 사이에 줄바꿈 두 번을 넣어 빈 줄 하나를 만듭니다
)
prompt_text = text_template.format(inquiry=new_inquiry)

print("=== 문자열 입력 ===")
print(prompt_text)
text_response = model.invoke(prompt_text)
print("=== 문자열 방식의 분류 ===")
print(text_response.text)

print("채팅 방식:", chat_response.text)
print("문자열 방식:", text_response.text)
