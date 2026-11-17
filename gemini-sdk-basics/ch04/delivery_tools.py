# 소스 경로: gemini-sdk-basics/ch04/delivery_tools.py
"""배송 데이터와 조회 함수, Gemini에 전달할 도구 설명을 정의합니다."""

from google.genai.interactions import FunctionParam

# 1. 주문 데이터의 운송장 번호와 연결되는 실습용 배송 정보입니다.
# 배송 중인 항목의 물류 거점 ID는 eta_tools.py의 도착 예정일 조회에 사용됩니다.
# 배송 완료 항목은 후속 도착 예정일 조회가 필요하지 않아 거점 ID를 넣지 않습니다.
DELIVERY_STATUS = {
    "TRK-7029": "배송 중, 현재 물류 거점 ID: HUB-SEOUL",
    "TRK-4186": "배송 완료",
}


def get_delivery_status(tracking_number: str) -> str:
    """운송장 번호로 실습용 배송 상태를 조회합니다."""
    # 2. 번호가 없으면 예외 대신 안내 문자열을 반환합니다. 실제 택배 API는 호출하지 않습니다.
    return DELIVERY_STATUS.get(tracking_number, "등록된 배송 정보가 없습니다.")


# 3. 모델에는 조회 코드 대신 함수 이름과 용도, 필요한 운송장 번호를 설명합니다.
# FunctionParam은 설명의 구조를 나타내는 타입 힌트이며, 함수를 자동 실행하지 않습니다.
get_delivery_status_tool: FunctionParam = {
    "type": "function",
    "name": "get_delivery_status",
    "description": "운송장 번호로 배송 상태와 현재 물류 거점 ID를 조회합니다.",
    "parameters": {
        "type": "object",
        "properties": {
            # 이 키는 get_delivery_status()의 매개변수 이름과 일치해야 합니다.
            "tracking_number": {
                "type": "string",
                "description": "운송장 번호. 예: TRK-7029",
            },
        },
        "required": ["tracking_number"],  # 배송 조회에는 운송장 번호가 필요합니다.
    },
}
