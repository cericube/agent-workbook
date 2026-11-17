"""고객 ID로 최근 주문번호를 조회하는 실습용 도구입니다."""

from google.genai.interactions import FunctionParam

# 1. 실제 고객 서비스 대신 고정 데이터를 사용합니다. 주문번호는 order_tools.py와 연결됩니다.
CUSTOMERS = {
    "CUST-001": {"name": "김민수", "recent_order_id": "ORD-1001"},
    "CUST-002": {"name": "이서연", "recent_order_id": "ORD-1002"},
}


def get_customer(customer_id: str) -> str:
    """고객명과 최근 주문번호를 반환합니다."""
    # 2. 고객 ID로 조회합니다. 등록되지 않은 ID이면 get()은 None을 반환합니다.
    customer = CUSTOMERS.get(customer_id)
    # 조회 실패도 문자열로 돌려주어 모델이 사용자에게 안내할 수 있게 합니다.
    if customer is None:
        return f"고객 ID {customer_id}에 해당하는 고객을 찾을 수 없습니다."
    # 최근 주문을 묻는 질문이면 모델은 이 주문번호로 get_order를 요청할 수 있습니다.
    # 여기에서 get_order를 직접 호출하지는 않습니다.
    return f"고객명: {customer['name']}, 최근 주문번호: {customer['recent_order_id']}"


# 3. 모델에 제공할 도구 설명입니다. 함수 코드는 보내지 않습니다.
# FunctionParam은 딕셔너리 구조를 나타내는 타입 힌트이며 함수를 자동 실행하지 않습니다.
get_customer_tool: FunctionParam = {
    "type": "function",
    "name": "get_customer",
    "description": "고객 ID로 고객명과 최근 주문번호를 조회합니다.",
    "parameters": {
        "type": "object",
        # 인자 이름은 get_customer의 매개변수 customer_id와 일치해야 합니다.
        "properties": {
            "customer_id": {"type": "string", "description": "고객 ID"},
        },
        "required": ["customer_id"],
    },
}
