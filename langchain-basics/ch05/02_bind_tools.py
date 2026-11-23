# 소스 경로: langchain-basics/ch05/02_bind_tools.py

import os

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


# 함수의 타입 힌트로 도구의 입력 스키마를 만들고, docstring을 도구 설명으로 사용합니다.
@tool
def add(a: int, b: int) -> int:
    """두 정수를 더한 결과를 반환합니다."""
    return a + b


# .env에서 설정을 불러옵니다. 이미 설정된 환경 변수는 우선합니다.
load_dotenv()

model_name = os.getenv("GEMINI_MODEL")
api_key = os.getenv("GEMINI_API_KEY")

if not model_name or not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")

# vertexai=False로 Gemini Developer API를 사용합니다.
# temperature를 낮추면 다음 토큰을 고를 때 무작위성이 줄어듭니다.
model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api_key,
    vertexai=False,
    temperature=0,
)

# 템플릿의 {a}와 {b}에 숫자를 채워 질문 문자열을 만듭니다.
prompt = PromptTemplate.from_template("{a}와 {b}을 더해 줘.")
prompt_text = prompt.format(a=12, b=8)
messages = [HumanMessage(content=prompt_text)]

# bind_tools()는 add의 이름, 설명, 입력 스키마를 모델에 전달하도록 설정합니다.
model_with_tools = model.bind_tools([add])

# invoke()는 완성된 질문과 도구 정의를 Gemini에 보내고 AIMessage를 받습니다.
# 모델이 add 사용을 요청하면 응답의 tool_calls에 a와 b의 값이 담깁니다.
response = model_with_tools.invoke(messages)

# tool_calls에는 모델이 요청한 도구 호출이 담깁니다. 실제 도구 실행은 별도 단계입니다.
# 각 요청의 name은 도구 이름, args는 실행 인수, id는 실행 결과를 연결할 식별자입니다.
# 모델이 도구 호출 없이 바로 답하면 빈 목록이 출력됩니다.
print("=== 도구 호출 요청 ===")
print(response.tool_calls)

# 도구 호출 요청 출력 예시입니다. id는 호출마다 달라질 수 있습니다.
# [
#     {
#         "name": "add",
#         "args": {"b": 8, "a": 12},
#         "id": "call_10906467441802470924",
#         "type": "tool_call",
#     }
# ]


# 실행할 수 있는 도구를 이름으로 등록합니다. 여기서는 "add"가 add 도구에 연결됩니다.
registered_tools = {add.name: add}

# 사용자 질문과 모델의 도구 호출 요청을 대화에 순서대로 보관합니다.
# 메시지를 언패킹 해서 넣는다.
conversation: list[BaseMessage] = [*messages, response]

# 모델이 보낸 호출 요청을 목록 순서대로 처리합니다. 목록이 비어 있으면 반복문을 건너뜁니다.
for tool_call in response.tool_calls:
    # 요청의 name으로 등록된 도구 객체를 찾습니다.
    selected_tool = registered_tools.get(tool_call["name"])
    # 이름이 등록되어 있지 않으면 실행할 도구를 찾을 수 없으므로 즉시 오류를 냅니다.
    if selected_tool is None:
        raise ValueError(f"등록되지 않은 도구: {tool_call['name']}")

    # args 딕셔너리의 키와 값을 함수의 인자 이름과 값으로 사용합니다.
    # 예를 들어 {"b": 8, "a": 12}가 들어오면 add에 a=12, b=8을 전달해 20을 얻습니다.
    result = selected_tool.invoke(tool_call["args"])
    print(f"{selected_tool.name} 계산 결과: {result}")

    # 실행 결과를 원래 호출 요청과 연결합니다.
    # tool_call_id=tool_call["id"]는 모델이 보낸 요청의 ID를 그대로 넣습니다.
    # 모델이 도구를 여러 번 호출해도 이 ID로 각 요청과 결과를 연결할 수 있습니다.
    conversation.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))

# 도구 호출 요청이 있으면 질문, 호출 요청, 실행 결과를 모델에 보내 최종 답변을 받습니다.
# 도구 호출 요청이 없으면 첫 번째 모델 응답을 최종 답변으로 사용합니다.

final_response = model.invoke(conversation) if response.tool_calls else response
print("최종 답변:", final_response.text)
