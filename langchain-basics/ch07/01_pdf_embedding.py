# 소스 경로: langchain-basics/ch07/01_pdf_embedding.py
# PDF에서 텍스트를 추출하고 검색에 쓸 벡터를 만들어 로컬 Chroma에 저장합니다.

import os
import shutil
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader
from pydantic import SecretStr

# pip install langchain-unstructured
# pip install "unstructured[pdf]"
# pip install langchain-chroma

# 본 예제에서는 PDF의 문장이 여러 페이지에 걸쳐 이어지더라도 페이지별로 분리된다고 가정하며, 페이지 간 문맥 연결은 처리하지 않습니다.

# 1. PDF 경로를 정하고 로더를 설정합니다.
# with_name()으로 스크립트 경로의 파일 이름을 바꿔 같은 디렉터리의 PDF를 찾습니다.
pdf_path = Path(__file__).with_name("technical-cognitive-intent-debt-ko.pdf")

# 이 로더는 아래 lazy_load()에서 PDF를 읽어 제목이나 문단 같은 요소를 반환합니다.
loader = UnstructuredLoader(
    file_path=str(pdf_path),  # PDF 경로를 문자열로 전달합니다.
    partition_via_api=False,  # Unstructured API 대신 현재 환경에서 PDF를 분석합니다.
    languages=["kor", "eng"],  # 분석에 사용할 언어 코드(한국어, 영어)
    strategy="fast",  # PDF에 이미 포함된 텍스트를 우선 추출합니다.
)

# 2. PDF 요소에서 추출한 텍스트를 원본 페이지별로 모읍니다.
# texts_by_page의 키는 PDF 페이지 번호이고, 값은 해당 페이지의 텍스트 문자열 목록입니다.
# defaultdict(list)는 새 페이지의 텍스트를 처음 추가할 때 빈 리스트를 만듭니다.
texts_by_page: dict[int, list[str]] = defaultdict(list)

# lazy_load()는 제목이나 문단 같은 요소를 Document로 하나씩 반환합니다.
for element in loader.lazy_load():
    # 앞뒤 공백을 제거한 뒤 텍스트가 남은 요소만 모읍니다.
    text = element.page_content.strip()
    if text:
        # 로더의 메타데이터에서 원본 페이지 번호를 읽어 그 페이지에 텍스트를 추가합니다.
        texts_by_page[element.metadata["page_number"]].append(text)

# 3. 텍스트가 있는 페이지를 번호순으로 정리해 페이지당 하나의 Document를 만듭니다.
# pages는 Document 목록입니다. 각 Document의 page_content에는 페이지 본문이,
# metadata에는 출처를 추적할 PDF 경로와 페이지 번호가 들어갑니다.
pages = [
    Document(
        # 요소 사이에 빈 줄을 넣어 경계를 표시합니다.
        page_content="\n\n".join(texts_by_page[page_number]),
        metadata={
            "source": str(pdf_path),  # 원본 PDF의 파일 경로
            "page_number": page_number,  # 1부터 시작하는 PDF 페이지 번호
            "page": page_number - 1,  # 0부터 시작하는 페이지 인덱스
        },
    )
    for page_number in sorted(texts_by_page)
]

# 4. 페이지 본문을 검색에 사용할 작은 조각으로 나눕니다.
# 빈 줄이나 줄바꿈을 우선 경계로 삼아 조각의 크기를 조절합니다.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # 조각 하나의 목표 최대 길이(문자 수)
    chunk_overlap=150,  # 문맥을 유지하기 위해 인접한 조각에 겹쳐 넣을 문자 수의 기준
)

# 페이지를 각각 나누므로 한 조각에 여러 페이지가 섞이지 않습니다.
# chunks는 Document 목록입니다. 각 조각은 나뉜 본문과 원본 페이지의 메타데이터를 담습니다.
chunks = text_splitter.split_documents(pages)
# 저장할 텍스트가 없으면 임베딩을 요청하기 전에 실행을 종료합니다.
if not chunks:
    raise SystemExit(f"{pdf_path.name}에서 추출할 수 있는 텍스트가 없습니다.")

print("문서 조각 개수:", len(chunks))

# 아래 미리보기 예제는 각 조각의 앞 100자를 출력합니다.
# 페이지 메타데이터에 category가 없으므로 이 항목은 None으로 출력됩니다.
# for i, doc in enumerate(chunks):
#     print(f"[{i}] {doc.metadata.get('category')}")
#     print(doc.page_content[:100])
#     print()


# 5. Gemini API 키를 읽고 임베딩 모델을 설정합니다.
# .env에서 환경 변수를 불러옵니다. 기본 설정에서는 이미 설정된 값이 우선합니다.
load_dotenv()

# GEMINI_API_KEY가 설정되어 있지 않거나 비어 있으면 실행을 종료합니다.
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")


# Gemini 임베딩에 사용할 모델과 인증 방식을 설정합니다.
# 문서 텍스트는 add_documents()에서 임베딩을 요청할 때 Gemini API로 전송됩니다.
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2",
    # SecretStr을 출력하면 키 값이 가려지고, API 인증에는 실제 값이 사용됩니다.
    api_key=SecretStr(api_key),
    # False로 지정하면 Gemini Developer API를 선택해 위 API 키로 인증합니다.
    vertexai=False,
)

# 6. 스크립트와 같은 디렉터리에 로컬 Chroma 저장소를 준비합니다.
# 기존 저장소 전체를 삭제하고 현재 PDF로 다시 만듭니다.
# chroma_db에 있던 다른 컬렉션도 함께 삭제됩니다.
db_path = Path(__file__).with_name("chroma_db")
if db_path.exists():
    shutil.rmtree(db_path)

vector_store = Chroma(
    # 문서와 벡터를 함께 관리할 컬렉션의 이름입니다.
    collection_name="langchain_07_gemini_embedding_2",
    # 저장할 문서 조각을 벡터로 변환하는 객체입니다.
    embedding_function=embeddings,
    # 다음 실행에서도 컬렉션을 열 수 있게 데이터를 로컬 디스크에 보관합니다.
    persist_directory=str(db_path),
)


# 7. 조각별로 ID를 부여하고 본문, 벡터, 메타데이터를 Chroma에 저장합니다.
# chunk_ids는 chunks와 같은 순서의 ID 목록입니다. ID는 PDF 파일명과 0부터 시작하는
# 조각 인덱스를 콜론으로 이어 만듭니다.
chunk_ids = [f"{pdf_path.name}:{index}" for index in range(len(chunks))]
# add_documents()는 Gemini에서 각 조각의 임베딩 벡터를 받아 지정된 ID로 저장합니다.
# 각 레코드에는 벡터, 조각 본문, 원본 PDF 경로와 페이지 번호가 들어갑니다.
vector_store.add_documents(chunks, ids=chunk_ids)

# 8. 텍스트가 있는 페이지 수, 저장한 조각 수, 로컬 저장 경로를 출력합니다.
print("텍스트를 추출한 페이지 수:", len(pages))
print("저장한 문서 조각 수:", len(chunks))
print("Chroma 저장 경로:", db_path)
