# 소스 경로: gemini-sdk-basics/ch03/01_json_response.py
"""2. 항목별 스키마 없이 JSON 객체로 응답받고 딕셔너리로 변환합니다."""

import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai.interactions import Interaction, TextResponseFormat

# 실제 주문을 조회하는 대신, 이 문장에 들어 있는 주문 정보를 추출합니다.
source_text = (
    "주문번호는 ORD-1001이고, 상품은 파이썬 입문서 2권입니다. 단가는 25,000원입니다."
)


def main():
    # .env의 값을 환경 변수로 불러옵니다. 이미 설정된 환경 변수는 그대로 사용합니다.
    load_dotenv()
    # API 키나 모델 이름이 없거나 비어 있으면 요청을 보내기 전에 실행을 중단합니다.
    if not os.environ.get("GEMINI_API_KEY") or not os.environ.get("GEMINI_MODEL"):
        raise RuntimeError(".env에 GEMINI_API_KEY와 GEMINI_MODEL을 설정해 주세요.")
    model = os.environ["GEMINI_MODEL"]

    # 환경 변수의 API 키로 클라이언트를 만들고, 블록을 벗어나면 연결을 닫습니다.
    with genai.Client() as client:
        # 추출할 항목과 원문을 함께 전달하고, 답변의 출력 형식을 지정합니다.
        response = client.interactions.create(
            model=model,
            input=(
                "다음 문장에서 주문번호, 상품명, 수량, 단가를 빠짐없이 추출해 "
                f"하나의 JSON 객체로 반환하세요. \n{source_text}"
            ),
            response_format=TextResponseFormat(
                # 텍스트 응답의 내용을 JSON 형식으로 받도록 설정합니다.
                type="text",
                mime_type="application/json",
                # 이 단계에서는 JSON 형식만 요청하고 schema_는 지정하지 않습니다.
                # 필요한 항목은 질문으로 요청하며, 키와 타입을 스키마로 고정하지 않습니다.
            ),
            stream=False,  # 스트리밍 이벤트 대신 응답 객체를 받습니다.
            store=False,  # 후속 대화 연결이나 조회를 위해 서버에 기록을 저장하지 않습니다.
        )

    # 일반 응답이 정상적으로 완료됐는지 확인한 뒤 JSON 문자열을 읽습니다.
    # 타입 검사 도구도 이 검사 이후에는 반환값을 Interaction 객체로 판단합니다.
    if not isinstance(response, Interaction):
        raise TypeError("일반 Interaction 응답이 필요합니다.")
    # 응답 객체를 받았더라도 생성이 완료됐고 텍스트가 있는지 따로 확인합니다.
    if response.status != "completed" or not response.output_text:
        raise RuntimeError(f"응답을 받지 못했습니다: {response.status}")

    print("응답 문자열:", response.output_text)
    # JSON 문자열을 Python 값으로 변환합니다. 이 예제에서는 객체가 딕셔너리로 바뀝니다.
    # 필요한 키나 수량의 범위는 검사하지 않으며, 문법이 잘못되면 JSONDecodeError가 발생합니다.
    data = json.loads(response.output_text)
    # JSON 문법이 맞아도 빈 객체가 올 수 있으므로, 추출 결과가 있는지 확인합니다.
    if not isinstance(data, dict) or not data:
        raise ValueError("주문 정보가 담긴 JSON 객체를 받지 못했습니다.")
    print(type(data))
    print(data)
    # product 또는 product_name 중 어떤 키가 올지 고정하지 않았으므로 전체 값만 출력합니다.


if __name__ == "__main__":
    # 이 파일을 직접 실행할 때만 API 요청을 보냅니다.
    main()
