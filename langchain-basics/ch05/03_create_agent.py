# 소스 경로: langchain-basics/ch05/03_create_agent.py

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
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


# tools에 등록한 add는 모델이 덧셈을 요청할 때 에이전트가 실행할 수 있습니다.
# system_prompt는 모든 질문에 적용할 도구 사용 기준과 답변 언어를 지정합니다.
agent = create_agent(
    model=model,
    tools=[add],
    system_prompt="덧셈 요청은 등록된 도구로 계산한 뒤 한국어로 답변하세요.",
)


# messages에 사용자 질문을 담습니다. role은 발신자, content는 질문 내용입니다.
# 모델이 도구 호출을 요청하면 에이전트가 도구를 실행하고 그 결과를 모델에 다시 전달합니다.
result = agent.invoke({"messages": [{"role": "user", "content": "12와 8을 더해 줘."}]})


# 반환된 대화 기록에서 ToolMessage만 골라 도구가 반환한 값을 출력합니다.
for message in result["messages"]:
    if isinstance(message, ToolMessage):
        print("도구 실행 결과:", message.content)

# 대화 기록의 마지막 메시지에서 모델의 최종 답변 텍스트를 꺼냅니다.
print("최종 답변:", result["messages"][-1].text)
