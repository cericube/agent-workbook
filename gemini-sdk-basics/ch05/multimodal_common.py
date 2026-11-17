# 소스 경로: gemini-sdk-basics/ch05/multimodal_common.py
"""질문과 작은 파일 하나를 Interactions API에 보내 텍스트 답변을 받습니다."""

import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai.interactions import Interaction

# 실행하는 터미널의 위치와 관계없이 ch05를 기준으로 파일을 찾습니다.
BASE_DIR = Path(__file__).resolve().parent


def ask_file(file_path: str, content_type: str, mime_type: str, question: str) -> str:
    """이미지·PDF·오디오·동영상 파일을 질문과 함께 전달합니다."""
    # 전체 흐름: 각 예제의 main() → ask_file의 1~5번 → 답변 문자열 반환 → 예제에서 출력.
    # 1. ch05/.env를 먼저 읽고, 부족한 설정은 상위 폴더의 .env에서 읽습니다.
    # 이미 설정된 환경 변수는 덮어쓰지 않습니다.
    load_dotenv(BASE_DIR / ".env")
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY") or not os.environ.get("GEMINI_MODEL"):
        raise RuntimeError(".env에 GEMINI_API_KEY와 GEMINI_MODEL을 설정해 주세요.")

    # 2. 경로 문자열만 전송하지 않고 Python에서 파일 내용을 직접 읽습니다.
    path = BASE_DIR / file_path
    if not path.is_file():
        raise FileNotFoundError(f"실습 파일을 준비해 주세요: {path}")
    # 파일이 없거나 비어 있으면 네트워크 요청 전에 오류로 중단합니다.
    file_bytes = path.read_bytes()
    if not file_bytes:
        raise ValueError(f"빈 파일은 분석할 수 없습니다: {path}")

    # 3. 파일 바이트를 요청에 담을 수 있는 Base64 문자열로 바꿉니다.
    # 파일 형식을 변환하는 과정은 아닙니다. mime_type은 실제 파일 형식과 같아야 합니다.
    # b64encode 결과는 바이트이므로 decode로 문자열을 만듭니다. 원본보다 데이터가 커집니다.
    encoded_data = base64.b64encode(file_bytes).decode("utf-8")

    # 4. 질문과 파일을 같은 input 목록에 넣고 한 번 요청합니다.
    print(f"[요청] {path.name} ({content_type}, {mime_type})", flush=True)
    # Files API로 파일을 업로드하지 않고 요청 본문에 직접 넣는 인라인 입력입니다.
    with genai.Client() as client:
        response = client.interactions.create(
            model=os.environ["GEMINI_MODEL"],
            # 첫 항목은 수행할 작업, 두 번째 항목은 분석할 자료입니다.
            input=[
                {"type": "text", "text": question},
                {
                    "type": content_type,
                    "mime_type": mime_type,
                    "data": encoded_data,  # 로컬 파일 경로가 아닌 파일 내용입니다.
                },
            ],
            stream=False,  # 스트리밍 대신 완성된 응답 객체를 받습니다.
            # Interaction 기록을 저장하지 않습니다. 모든 내부 로그의 즉시 삭제를 뜻하지는 않습니다.
            store=False,
        )
    # with를 벗어나면 클라이언트 연결을 닫습니다. 로컬 원본 파일은 삭제하지 않습니다.
    # Files API 업로드 파일이 없으므로 업로드 파일 삭제 요청도 필요하지 않습니다.

    # 5. 응답 객체, 완료 상태, 답변 텍스트를 확인한 뒤 호출한 예제에 반환합니다.
    if not isinstance(response, Interaction):
        raise TypeError("Interaction 응답이 필요합니다.")
    # 함수 호출이나 후속 대화 없이 텍스트 답변 하나를 받는 예제입니다.
    # 정상 완료가 아니거나 텍스트가 비어 있으면 답변 대신 오류를 알립니다.
    if response.status != "completed" or not response.output_text:
        raise RuntimeError(f"답변을 받지 못했습니다: {response.status}")
    return response.output_text
