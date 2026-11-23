# 소스 경로: langchain-basics/ch06/01_embedding.py
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import SecretStr

# 이 스크립트와 같은 디렉터리에 있는 텍스트 파일을 읽습니다.
text_path = Path(__file__).with_name("langchain_intro.txt")
documents = [
    Document(
        page_content=text_path.read_text(encoding="utf-8"),
        metadata={"source": str(text_path)},  # 원본 파일 경로를 출처로 기록합니다.
    )
]

print("원본 문서 개수:", len(documents))
print(documents)

# 문단, 줄바꿈, 공백 순으로 경계를 찾아 긴 텍스트를 나눕니다.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,  # 조각 하나의 최대 문자 수입니다.
    chunk_overlap=30,  # 앞뒤 조각의 문맥을 이어 주는 목표 겹침 문자 수입니다.
)
# 각 조각을 Document로 만들고 원본의 metadata를 복사합니다.
chunks = text_splitter.split_documents(documents)
print("문서 조각 개수:", len(chunks))
for chunk in chunks:
    print("\n", chunk)


# .env의 설정을 환경 변수로 불러오고 API 키가 없거나 비어 있으면 종료합니다.
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")

# 임베딩 요청에 사용할 모델과 인증 정보를 설정합니다.
# 문서 본문을 벡터로 변환하는 API 요청은 아래 embed_documents()에서 보냅니다.
embeddings = GoogleGenerativeAIEmbeddings(
    # Gemini API가 텍스트를 수치 벡터로 변환할 때 사용할 모델의 이름입니다.
    model="gemini-embedding-2",
    # 환경 변수에서 읽은 키를 라이브러리가 받는 SecretStr 타입으로 감쌉니다.
    # SecretStr을 출력하면 키 값이 가려지고, API 인증에는 실제 값이 사용됩니다.
    api_key=SecretStr(api_key),
    # False로 지정하면 Gemini Developer API를 선택해 위 API 키로 인증합니다.
    vertexai=False,
)

# 각 조각의 본문만 API에 보내고 본문마다 실수 리스트 하나를 받습니다.
texts = [chunk.page_content for chunk in chunks]
vectors = embeddings.embed_documents(texts)

print("벡터 개수:", len(vectors))
for vector in vectors:
    # 벡터의 타입을 확인하고 출력이 길어지지 않도록 앞쪽 값 5개를 표시합니다.
    print(type(vector), vector[:5], "...")
