# 소스 경로: gemini-sdk-basics/ch05/pdf_example.py
"""PDF 형식의 IT 기술 리포트에서 기술 동향과 주요 시사점을 정리합니다."""

from multimodal_common import ask_file


def main():
    # 1. 공통 함수에 질문과 파일 정보를 전달합니다. 파일 읽기와 API 요청은 ask_file이 수행합니다.
    # file_path는 이 예제와 같은 폴더인 ch05를 기준으로 지정합니다.
    answer = ask_file(
        file_path="samples/report.pdf",
        # content_type은 입력 종류, mime_type은 실제 파일 형식을 나타냅니다.
        content_type="document",
        mime_type="application/pdf",
        # 리포트 요약과 근거 페이지, IT 용어 설명을 요청합니다. 페이지 표시는 원본과 비교합니다.
        question=(
            "기술 보고서의 핵심 내용을 한국어로 직관적이고 간결하게 요약해 주세요. "
            "핵심 내용의 근거 근거 페이지를 표시하세요. "
            "이어서 주요 IT 용어와 약어는 간단히 정리 하세요. "
        ),
    )
    # 2. 공통 함수가 완료 상태와 텍스트를 확인해 반환한 답변을 출력합니다.
    print(answer)


# 실행 진입점입니다. 직접 실행하면 main()의 1번부터 시작하며, import만 하면 API를 호출하지 않습니다.
if __name__ == "__main__":
    main()
