"""상품별 반품 조건을 조회하는 실습용 도구입니다."""

from google.genai.interactions import FunctionParam

# 1. 실제 판매 정책이 아닌 실습용 데이터입니다. 키는 order_tools.py의 상품명과 같습니다.
RETURN_POLICIES = {
    "파이썬 입문서": "수령 후 7일 이내, 훼손이나 필기가 없는 경우 반품 가능",
    "USB 케이블": "수령 후 7일 이내, 포장을 개봉하지 않은 경우 반품 가능",
}


def get_return_policy(product: str) -> str:
    """주문 조회에서 얻은 상품명으로 반품 조건을 조회합니다."""
    # 2. 해당 상품의 조건을 반환합니다. 등록되지 않은 상품도 안내 문자열로 반환합니다.
    # 조건 조회만 하며 실제 반품 접수나 주문 변경은 하지 않습니다.
    return RETURN_POLICIES.get(product, "등록된 반품 조건이 없습니다.")


# 3. 주문 조회에서 얻은 상품명을 인자로 받는 도구 설명입니다.
# 주문 조회 후에는 배송 조회와 반품 조건 조회가 서로의 결과를 기다릴 필요가 없습니다.
get_return_policy_tool: FunctionParam = {
    "type": "function",
    "name": "get_return_policy",
    "description": "주문 조회 결과의 상품명으로 반품 가능 기간과 조건을 조회합니다.",
    "parameters": {
        "type": "object",
        # 이 이름은 get_return_policy의 매개변수 product와 일치해야 합니다.
        "properties": {
            "product": {"type": "string", "description": "주문 조회 결과의 상품명"},
        },
        "required": ["product"],
    },
}
