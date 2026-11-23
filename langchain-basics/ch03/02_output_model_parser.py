# 소스 경로: langchain-basics/ch03/02_output_model_parser.py

import os

from dotenv import load_dotenv
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.output_parsers import (
    JsonOutputParser,
    PydanticOutputParser,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

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


# 두 파서가 출력 형식을 안내할 때 사용하는 공통 상품 스키마입니다.
class Product(BaseModel):
    name: str = Field(description="상품명")
    storage_gb: int = Field(gt=0, description="저장 용량(GB)")
    price_krw: int = Field(ge=0, description="가격(원)")


DESCRIPTION: str = "삼성 갤럭시 S25는 저장 용량이 256GB이며 가격은 115만 원입니다."
EXTRACTION_TASK: str = (
    "상품명, 저장 용량, 가격을 추출하세요. "
    "저장 용량은 GB 단위 정수, 가격은 원 단위 정수로 반환하세요."
)
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


# JSON을 읽은 뒤 필드 타입과 값의 범위를 검증해 Product 인스턴스를 생성합니다.
# 검증에 실패하면 OutputParserException이 발생합니다.
def run_pydantic_parser() -> None:
    parser: PydanticOutputParser[Product] = PydanticOutputParser(
        pydantic_object=Product
    )
    message: list[BaseMessage] = make_messages(
        EXTRACTION_TASK,
        parser.get_format_instructions(),
    )
    response: AIMessage = model.invoke(message)
    result: Product = parser.invoke(response)
    show_result("PydanticOutputParser", result)


# Product 스키마는 프롬프트의 출력 형식 안내에 쓰입니다.
# 파싱 결과는 JSON에서 읽은 값이며, Product의 필드 제약은 검증하지 않습니다.
def run_json_parser() -> None:
    parser: JsonOutputParser = JsonOutputParser(pydantic_object=Product)
    message: list[BaseMessage] = make_messages(
        EXTRACTION_TASK, parser.get_format_instructions()
    )
    response: AIMessage = model.invoke(message)
    result: object = parser.invoke(response)
    show_result("JsonOutputParser[Model]", result)


# 같은 응답으로 두 파서의 검증 동작을 비교하므로 Gemini API를 호출하지 않습니다.
def run_model_parser_error() -> None:
    pydantic_parser: PydanticOutputParser[Product] = PydanticOutputParser(
        pydantic_object=Product
    )
    json_parser: JsonOutputParser = JsonOutputParser(pydantic_object=Product)
    # 필수 필드인 price_krw를 뺀 JSON을 만들어 필드 누락을 재현합니다.
    response = AIMessage(content='{"name": "삼성 갤럭시 S25", "storage_gb": 256}')
    result: object = json_parser.invoke(response)
    show_result("JsonOutputParser[Model]", result)

    # Pydantic 파서의 검증 실패는 OutputParserException으로 전달됩니다.
    try:
        pydantic_parser.invoke(response)
    except OutputParserException as error:
        print(type(error).__name__)


run_pydantic_parser()
run_json_parser()
run_model_parser_error()
