# 소스 경로: langchain-basics/ch03/01_output_parser.py

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.output_parsers import (
    CommaSeparatedListOutputParser,
    JsonOutputParser,
    StrOutputParser,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model_name: str | None = os.getenv("GEMINI_MODEL")
api_key: str | None = os.getenv("GEMINI_API_KEY")

if not model_name or not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")

model: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api_key,
    vertexai=False,  # Gemini Developer API 사용
)

DESCRIPTION: str = "삼성 갤럭시 S25는 저장 용량이 256GB이며 가격은 115만 원입니다."
EXTRACTION_TASK: str = (
    "상품명, 저장 용량, 가격을 추출하세요. "
    "저장 용량은 GB 단위 정수, 가격은 원 단위 정수로 반환하세요."
)
# 모든 예제에서 같은 상품 설명을 사용하고, 요청과 출력 형식 지시를 바꿉니다.
PROMPT: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        ("system", "주어진 상품 설명만 근거로 답하세요."),
        ("human", "{task}\n\n상품 설명:{description}\n\n{format_instructions}"),
    ]
)


def make_messages(task: str, format_instructions: str = "") -> list[BaseMessage]:
    return PROMPT.format_messages(
        task=task, description=DESCRIPTION, format_instructions=format_instructions
    )


def show_result(label: str, result: object) -> None:
    print(f"\n{label} {type(result).__name__}")
    print(result)


# 한 문장 요약은 프롬프트에서 요청합니다. 파서는 응답에서 텍스트만 꺼냅니다.
def run_str_parser() -> None:
    parser: StrOutputParser = StrOutputParser()
    messages: list[BaseMessage] = make_messages(
        "상품 설명을 한국어 한 문장으로 요약하세요."
    )
    response: AIMessage = model.invoke(messages)
    result: str = parser.invoke(response)
    show_result("StrOutputParser", result)


# 응답을 JSON으로 파싱합니다. 이 예제에서는 Product 필드와 제약 조건을 검증하지 않습니다.
def run_json_parser() -> None:
    parser: JsonOutputParser = JsonOutputParser()
    message: list[BaseMessage] = make_messages(
        EXTRACTION_TASK, parser.get_format_instructions()
    )
    response: AIMessage = model.invoke(message)
    result: object = parser.invoke(response)
    show_result("JsonOutputParser", result)


# 쉼표로 구분된 응답을 문자열 목록으로 변환합니다. 숫자 항목도 문자열로 읽습니다.
def run_comma_parser() -> None:
    parser: CommaSeparatedListOutputParser = CommaSeparatedListOutputParser()
    message: list[BaseMessage] = make_messages(
        EXTRACTION_TASK, parser.get_format_instructions()
    )
    response: AIMessage = model.invoke(message)
    result: list[str] = parser.invoke(response)
    show_result("CommaSeparatedListOutputParser", result)


# 비교할 예제의 호출을 활성화하면 해당 파서의 결과를 확인할 수 있습니다.
run_str_parser()
run_json_parser()
run_comma_parser()
