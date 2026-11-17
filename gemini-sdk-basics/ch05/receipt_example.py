# 소스 경로: gemini-sdk-basics/ch05/receipt_example.py
"""영수증의 결제 날짜와 최종 합계를 읽습니다."""

from multimodal_common import ask_file


def main():
    # 1. 공통 함수에 질문과 파일 정보를 전달합니다. 파일 읽기와 API 요청은 ask_file이 수행합니다.
    # file_path는 이 예제와 같은 폴더인 ch05를 기준으로 지정합니다.
    answer = ask_file(
        file_path="samples/receipt.jpg",
        # content_type은 입력 종류, mime_type은 실제 파일 형식을 나타냅니다.
        content_type="image",
        mime_type="image/jpeg",
        # 상품별 가격이 아닌 최종 결제 금액을 요청하며, 읽기 어려운 항목의 응답 방식도 지정합니다.
        question=(
            "영수증에서 결제 날짜와 최종 합계 금액을 찾아 주세요. "
            "날짜: YYYY-MM-DD, 합계: 숫자원 형식으로 두 줄로 답하세요. "
            "읽을 수 없는 항목은 '확인 불가'라고 적으세요."
        ),
    )
    # 날짜와 금액은 JSON 객체가 아닌 일반 텍스트로 반환되므로 원본과 비교합니다.
    # 2. 공통 함수가 완료 상태와 텍스트를 확인해 반환한 답변을 출력합니다.
    print(answer)


# 실행 진입점입니다. 직접 실행하면 main()의 1번부터 시작하며, import만 하면 API를 호출하지 않습니다.
if __name__ == "__main__":
    main()
