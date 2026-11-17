# 소스 경로: gemini-sdk-basics/ch05/video_example.py
"""강의 영상의 핵심 개념과 주요 내용을 요약하고 정리합니다."""

from multimodal_common import ask_file


def main():
    # 1. 공통 함수에 질문과 파일 정보를 전달합니다. 파일 읽기와 API 요청은 ask_file이 수행합니다.
    # file_path는 이 예제와 같은 폴더인 ch05를 기준으로 지정합니다.
    answer = ask_file(
        file_path="samples/lecture.webm",
        # content_type은 입력 종류, mime_type은 실제 파일 형식을 나타냅니다.
        content_type="video",
        # 현재 경로는 .webm입니다. 아래 MIME 값은 실제 파일 형식에 맞는지 확인해야 합니다.
        mime_type="video/mp4",
        # 화면과 음성으로 강의를 요약하고, 복습할 위치를 찾을 수 있도록 시작 시간도 요청합니다.
        question=(
            "영상의 화면과 음성을 참고해 강의 내용을 한국어로 요약해 주세요. "
            "먼저 강의 전체를 세 문장 이내로 요약하고, "
            "'주제별 주요 내용', '핵심 개념과 용어', '예제 및 실습', "
            "'복습할 핵심 사항'으로 나누어 정리하세요. "
            "주제별 주요 내용에는 영상 시작을 00:00으로 한 시작 시간을 "
            "MM:SS 형식으로 함께 적으세요. "
            "강의에 없는 내용은 추가하지 말고, 확인하기 어려운 내용은 "
            "'확인 불가', 예제나 실습이 없으면 '없음'으로 표시하세요."
        ),
    )
    # 2. 공통 함수가 완료 상태와 텍스트를 확인해 반환한 답변을 출력합니다.
    print(answer)


# 실행 진입점입니다. 직접 실행하면 main()의 1번부터 시작하며, import만 하면 API를 호출하지 않습니다.
if __name__ == "__main__":
    main()
