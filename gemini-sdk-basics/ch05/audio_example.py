# 소스 경로: gemini-sdk-basics/ch05/audio_example.py
"""전화 통화 녹음에서 핵심 내용과 후속 조치를 정리합니다."""

from multimodal_common import ask_file


def main():
    # 1. 공통 함수에 질문과 파일 정보를 전달합니다. 파일 읽기와 API 요청은 ask_file이 수행합니다.
    # file_path는 이 예제와 같은 폴더인 ch05를 기준으로 지정합니다.
    answer = ask_file(
        file_path="samples/meeting.m4a",
        # content_type은 입력 종류, mime_type은 실제 파일 형식을 나타냅니다.
        content_type="audio",
        # 현재 경로는 .m4a입니다. 아래 MIME 값은 실제 파일 형식에 맞는지 확인해야 합니다.
        mime_type="audio/wav",
        # 통화 목적과 합의 사항을 구분하고, 녹음에 없는 담당자나 기한을 추측하지 않도록 요청합니다.
        question=(
            "전화 통화 내용을 한국어로 요약해 주세요. "
            "'통화 목적', '주요 내용', '요청 및 합의 사항', '후속 조치'로 나누어 정리하세요. "
            "후속 조치의 담당자와 기한은 통화에서 명확히 들리는 경우에만 적으세요. "
            "언급되지 않은 항목은 '언급 없음', 알아듣기 어려운 내용은 '확인 불가'로 표시하고 "
            "추측하지 마세요."
        ),
    )
    # 2. 공통 함수가 완료 상태와 텍스트를 확인해 반환한 답변을 출력합니다.
    print(answer)


# 실행 진입점입니다. 직접 실행하면 main()의 1번부터 시작하며, import만 하면 API를 호출하지 않습니다.
if __name__ == "__main__":
    main()
