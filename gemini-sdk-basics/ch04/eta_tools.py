"""물류 거점별 도착 예정일을 조회하는 실습용 도구입니다."""

from google.genai.interactions import FunctionParam

# 1. 실제 날짜 계산 대신 고정된 실습 데이터를 사용합니다.
# 키는 배송 조회 결과의 물류 거점 ID입니다. 시스템 날짜나 외부 배송 API를 사용하지 않습니다.
DELIVERY_ETA = {
    "HUB-SEOUL": "실습 기준 다음 날 오후 도착 예정",
    "HUB-BUSAN": "실습 기준 이틀 뒤 도착 예정",
}


def get_delivery_eta(hub_id: str) -> str:
    """배송 조회에서 얻은 물류 거점 ID로 도착 예정일을 조회합니다."""
    # 2. 거점 ID에 해당하는 예정일을 반환합니다. 없는 ID도 안내 문자열로 반환합니다.
    return DELIVERY_ETA.get(hub_id, "등록된 도착 예정 정보가 없습니다.")


# 3. 모델이 배송 조회 결과에서 hub_id를 얻어 이 도구를 요청할 수 있도록 설명합니다.
# description은 모델이 참고할 설명이며, Python의 실행 조건을 강제하는 코드는 아닙니다.
get_delivery_eta_tool: FunctionParam = {
    "type": "function",
    "name": "get_delivery_eta",
    "description": (
        "배송 조회 결과의 물류 거점 ID로 도착 예정일을 조회합니다. "
        "배송이 완료된 경우에는 조회할 필요가 없습니다."
    ),
    "parameters": {
        "type": "object",
        # 이 이름은 get_delivery_eta의 매개변수 hub_id와 일치해야 합니다.
        "properties": {
            "hub_id": {
                "type": "string",
                "description": "배송 조회 결과에 포함된 물류 거점 ID",
            },
        },
        "required": ["hub_id"],
    },
}
