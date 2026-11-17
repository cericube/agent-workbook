# 소스 경로: gemini-sdk-basics/ch04/order_tools.py
"""주문 데이터와 조회 함수, Gemini에 전달할 도구 설명을 정의합니다."""

from google.genai.interactions import FunctionParam

# 1. 실제 주문 서비스 대신 고정된 실습 데이터를 사용합니다.
ORDERS = {
    "ORD-1001": {"product": "파이썬 입문서", "tracking_number": "TRK-7029"},
    "ORD-1002": {"product": "USB 케이블", "tracking_number": "TRK-4186"},
}


def get_order(order_id: str) -> str:
    """주문번호로 상품명과 운송장 번호를 조회합니다."""
    # 2. 주문번호를 키로 조회합니다. 없으면 get()이 None을 반환합니다.
    order = ORDERS.get(order_id)
    if order is None:
        # 조회 실패도 문자열로 반환해 Gemini가 사용자에게 안내할 수 있게 합니다.
        return f"주문번호 {order_id}에 해당하는 주문을 찾을 수 없습니다."
    # 상품명은 반품 조건 조회에, 운송장 번호는 배송 조회에 사용할 수 있습니다.
    # 다음 함수를 여기에서 실행하지 않고, 두 값을 모델에게 돌려줍니다.
    return f"상품명: {order['product']}, 운송장 번호: {order['tracking_number']}"


# 3. 함수 코드는 Python에서 실행하고, 이름과 용도, 인자 설명은 Gemini에 전달합니다.
# FunctionParam은 도구 설명 딕셔너리의 구조를 나타내는 타입 힌트입니다.
# properties의 인자 이름은 Python 함수의 매개변수 이름과 같아야 합니다.
get_order_tool: FunctionParam = {
    "type": "function",  # Python 프로그램이 실행하는 함수 도구입니다.
    "name": "get_order",  # Gemini가 호출 요청에 넣을 함수 이름입니다.
    # 모델이 이 도구가 필요한지 판단할 때 참고하는 설명입니다.
    "description": "주문번호로 상품명과 운송장 번호를 조회합니다.",
    "parameters": {
        "type": "object",  # 인자는 키와 값으로 구성된 객체로 받습니다.
        "properties": {
            "order_id": {"type": "string", "description": "주문번호. 예: ORD-1001"},
        },
        "required": ["order_id"],  # properties에 정의한 인자를 필수로 지정합니다.
    },
}
