# 소스 경로: gemini-sdk-basics/ch03/02_json_schema.py
"""3. JSON Schema로 주문 정보의 키와 값 타입을 정합니다."""

import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai.interactions import Interaction, TextResponseFormat

# 실제 주문 시스템을 조회하지 않고, 이 문장에 적힌 주문 정보를 추출합니다.
source_text = (
    "주문번호는 ORD-1001이고, 상품은 파이썬 입문서 2권입니다. 단가는 25,000원입니다."
)

# 모델이 반환할 JSON의 키 이름과 값 타입을 정합니다.
order_schema = {
    "type": "object",  # 최상위 값은 키와 값으로 구성된 JSON 객체입니다.
    # properties에는 각 키의 타입과 의미를 적습니다. 이것만으로 필수가 되지는 않습니다.
    "properties": {
        "order_id": {"type": "string", "description": "주문번호"},
        "product": {"type": "string", "description": "상품명"},
        # minimum은 허용하는 최솟값입니다. 수량은 1 이상, 단가는 0 이상으로 요청합니다.
        "quantity": {"type": "integer", "minimum": 1, "description": "주문 수량"},
        "unit_price": {"type": "integer", "minimum": 0, "description": "원 단위 단가"},
    },
    "required": ["order_id", "product", "quantity", "unit_price"],  # 네 키 모두 필수
    "additionalProperties": False,  # properties에 없는 키는 허용하지 않습니다.
}


def main():
    # .env의 값을 환경 변수로 불러옵니다. 이미 설정된 값은 그대로 사용합니다.
    load_dotenv()
    # API 키나 모델 이름이 없거나 비어 있으면 요청 전에 실행을 중단합니다.
    if not os.environ.get("GEMINI_API_KEY") or not os.environ.get("GEMINI_MODEL"):
        raise RuntimeError(".env에 GEMINI_API_KEY와 GEMINI_MODEL을 설정해 주세요.")
    model = os.environ["GEMINI_MODEL"]

    # 블록을 벗어나면 API 요청에 사용한 클라이언트 연결을 닫습니다.
    with genai.Client() as client:
        response = client.interactions.create(
            model=model,
            input=f"다음 문장에서 주문 정보를 추출하세요.\n{source_text}",
            # JSON 형식과 함께 앞에서 정의한 출력 구조를 전달합니다.
            response_format=TextResponseFormat(
                type="text",
                mime_type="application/json",
                schema_=order_schema,  # SDK에서 출력 스키마를 받는 매개변수
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

    # 스키마는 모델의 출력 구조를 지정합니다. json.loads() 자체는 스키마를 검증하지 않습니다.
    order = json.loads(response.output_text)
    # 지정한 키 이름으로 값을 꺼냅니다. JSON 객체는 Python 딕셔너리로 변환됩니다.
    print(order["product"])
    print(order["quantity"])
    print(order)


if __name__ == "__main__":
    # 이 파일을 직접 실행할 때만 API 요청을 보냅니다.
    main()
