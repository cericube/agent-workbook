# 소스 경로: gemini-sdk-basics/ch05/image_example.py
"""사진에 보이는 물건을 설명합니다."""

from multimodal_common import ask_file


def main():
    # 1. 공통 함수에 질문과 파일 정보를 전달합니다. 파일 읽기와 API 요청은 ask_file이 수행합니다.
    # file_path는 이 예제와 같은 폴더인 ch05를 기준으로 지정합니다.
    answer = ask_file(
        file_path="samples/desk.jpg",
        # content_type은 입력 종류, mime_type은 실제 파일 형식을 나타냅니다.
        content_type="image",
        mime_type="image/jpeg",
        # 사진의 물건을 묻는 질문입니다. 같은 사진도 question을 바꾸면 글자나 장면을 물을 수 있습니다.
        question="사진에 보이는 물건을 세 가지 이내로 설명해 주세요.",
    )
    # 2. 공통 함수가 완료 상태와 텍스트를 확인해 반환한 답변을 출력합니다.
    print(answer)


# 실행 진입점입니다. 직접 실행하면 main()의 1번부터 시작하며, import만 하면 API를 호출하지 않습니다.
if __name__ == "__main__":
    main()
