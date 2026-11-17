# 소스 경로: gemini-sdk-basics/ch03/03_pydantic_response.py
"""4. Pydantic 모델로 스키마를 만들고 실제 JSON 응답을 검증합니다."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai.interactions import Interaction, TextResponseFormat
from pydantic import BaseModel, ConfigDict, Field

# 실제 주문을 조회하지 않고, 이 문장에 적힌 정보를 정해진 구조로 추출합니다.
source_text = (
    "주문번호는 ORD-1001이고, 상품은 파이썬 입문서 0권입니다. 단가는 25,000원입니다."
)


# BaseModel을 상속해 응답의 필드와 검증 규칙을 정의합니다.
# 이 클래스는 요청할 JSON Schema를 생성할 때와 실제 응답을 검증할 때 모두 사용합니다.
class OrderInfo(BaseModel):
    # 정의하지 않은 필드가 들어오면 검증 오류로 처리합니다.
    model_config = ConfigDict(extra="forbid")

    # 기본값을 지정하지 않았으므로 네 필드 모두 필수입니다.
    # description은 스키마에 포함되어 모델이 각 필드의 의미를 이해하는 데 사용됩니다.
    order_id: str = Field(description="주문번호")
    product: str = Field(description="상품명")
    # ge는 해당 값 이상이어야 한다는 뜻입니다. 수량은 1 이상, 단가는 0 이상입니다.
    quantity: int = Field(ge=1, description="주문 수량")
    unit_price: int = Field(ge=0, description="원 단위 단가")


def main():
    # .env의 값을 환경 변수로 불러옵니다. 이미 설정된 값은 그대로 사용합니다.
    load_dotenv()
    # 필수 설정이 없거나 비어 있으면 API 요청 전에 실행을 중단합니다.
    if not os.environ.get("GEMINI_API_KEY") or not os.environ.get("GEMINI_MODEL"):
        raise RuntimeError(".env에 GEMINI_API_KEY와 GEMINI_MODEL을 설정해 주세요.")
    model = os.environ["GEMINI_MODEL"]

    # 블록을 벗어나면 요청에 사용한 클라이언트 연결을 닫습니다.
    with genai.Client() as client:
        response = client.interactions.create(
            model=model,
            input=f"다음 문장에서 주문 정보를 추출하세요.\n{source_text}",
            # 답변을 JSON 형식으로 받고, OrderInfo에서 만든 출력 구조를 함께 전달합니다.
            response_format=TextResponseFormat(
                type="text",
                mime_type="application/json",
                # 필드 타입과 필수 여부, 최솟값 등을 JSON Schema 딕셔너리로 만듭니다.
                # 출력 구조를 요청하는 단계이며, 아직 실제 응답을 검증하는 것은 아닙니다.
                schema_=OrderInfo.model_json_schema(),
            ),
            stream=False,  # 스트리밍 이벤트 대신 응답 객체를 받습니다.
            store=False,  # 후속 대화 연결이나 조회를 위해 서버에 기록을 저장하지 않습니다.
        )

    # 일반 응답이 정상적으로 완료됐는지 확인한 뒤 JSON 문자열을 읽습니다.
    if not isinstance(response, Interaction):
        raise TypeError("일반 Interaction 응답이 필요합니다.")
    # 응답 객체를 받았더라도 생성 완료 여부와 텍스트 유무는 따로 확인합니다.
    if response.status != "completed" or not response.output_text:
        raise RuntimeError(f"응답을 받지 못했습니다: {response.status}")

    print(response.output_text)  # 검증 전 Gemini가 반환한 JSON
    # 받은 JSON을 검증하고 OrderInfo 객체로 만듭니다.
    # strict=True이므로 수량이 문자열 "2"이면 정수로 자동 변환하지 않고 오류를 발생시킵니다.
    # 필수 필드가 없거나 값이 규칙에 맞지 않으면 Pydantic의 ValidationError가 발생합니다.
    order = OrderInfo.model_validate_json(response.output_text, strict=True)
    # 검증을 통과한 객체는 딕셔너리의 키 대신 속성으로 값을 읽을 수 있습니다.
    print(order.product)
    print(order.quantity)
    print(order.model_dump())  # OrderInfo 객체를 일반 Python 딕셔너리로 변환합니다.
    # 구조와 값의 범위를 검증하더라도 실제 주문 정보가 맞는지는 별도로 확인해야 합니다.


if __name__ == "__main__":
    # 이 파일을 직접 실행할 때만 API 요청을 보냅니다.
    main()
