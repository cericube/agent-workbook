# 소스 경로: langchain-basics/ch07/02_chroma_similarity_search.py
# 기존 Chroma 컬렉션에서 질문과 유사한 PDF 조각을 검색합니다.
# 벡터 저장소 직접 검색, Retriever 호출, LCEL로 프롬프트 구성 순서로 실행됩니다.

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr

# 실행한 디렉터리와 관계없이 이 파일 옆의 chroma_db를 사용합니다.
# 이전 예제에서 생성하는 SQLite 파일이 없으면 검색을 시작하기 전에 종료합니다.
db_path = Path(__file__).with_name("chroma_db")
if not (db_path / "chroma.sqlite3").is_file():
    raise SystemExit(
        "Chroma 저장소가 없습니다. 먼저 01_pdf_embedding.py를 실행해 주세요."
    )

# .env의 값을 환경 변수로 읽습니다. 이미 설정된 환경 변수의 값이 우선합니다.
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit(".env에 GEMINI_API_KEY를 설정해 주세요.")

# 저장된 문서 벡터와 질문 벡터를 비교하기 위해 저장할 때와 같은 모델을 씁니다.
# vertexai=False는 Gemini Developer API를 사용하도록 지정합니다.
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2",
    api_key=SecretStr(api_key),
    vertexai=False,
)
# 01_pdf_embedding.py가 저장한 경로와 컬렉션 이름으로 기존 컬렉션을 엽니다.
# create_collection_if_not_exists=False는 컬렉션 이름이 없을 때 오류를 발생시킵니다.
vector_store = Chroma(
    collection_name="langchain_07_gemini_embedding_2",
    embedding_function=embeddings,
    persist_directory=str(db_path),
    create_collection_if_not_exists=False,
)

query = "인지적 의도 부채란 무엇인가요?"
# # 검색할 때 질문을 Gemini API로 보내 벡터로 바꾼 뒤, Chroma에서 가까운 조각을
# # 최대 3개 찾아 Document 목록으로 반환합니다.
# similar_docs = vector_store.similarity_search(query, k=3)

# # Document의 page_content에는 조각 본문이, metadata에는 저장할 때 기록한
# # PDF 경로와 1부터 시작하는 페이지 번호가 들어 있습니다.
# print("검색 질문:", query)
# for rank, doc in enumerate(similar_docs, start=1):
#     source = Path(doc.metadata["source"]).name
#     page_number = doc.metadata["page_number"]
#     print(f"\n[{rank}] {source} ({page_number}페이지)")
#     print(doc.page_content)

# Retriever는 질문 문자열을 받아 Document 목록을 반환하는 LangChain 실행 단위입니다.
# 여기서는 직접 검색과 같은 유사도 방식과 결과 개수 제한을 적용합니다.
# as_retriever()는 옵션을 설정하고, invoke()가 실제 검색을 실행합니다.
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
retrieved_docs = retriever.invoke(query)

print("\nRetriever 검색 질문:", query)
for rank, doc in enumerate(retrieved_docs, start=1):
    source = Path(doc.metadata["source"]).name
    page_number = doc.metadata["page_number"]
    print(f"\n[{rank}] {source} ({page_number}페이지)")
    print(doc.page_content)


print("\n======================================================================")


# 이 실습은 검색 결과와 원래 질문을 넣어 프롬프트 메시지를 만들고,
# 완성된 메시지의 내용을 출력하는 데까지 진행합니다.
# {context}에는 검색한 조각을 합친 문자열이, {question}에는 원래 질문이 들어갑니다.
prompt = ChatPromptTemplate.from_template(
    "아래 참고 문서를 바탕으로 질문에 답해 주세요.\n\n"
    "참고 문서:\n{context}\n\n질문: {question}"
)


# Retriever가 반환한 문서들의 본문을 검색 순서대로 이어 붙입니다.
# 조각 사이에 빈 줄을 넣어 프롬프트에서 각 조각의 경계를 읽기 쉽게 합니다.
def format_documents(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


# LCEL의 | 연산자는 앞 단계의 출력을 뒤 단계의 입력으로 연결합니다.
# 딕셔너리의 두 경로는 같은 질문 문자열을 입력으로 받습니다.
# context 경로는 Retriever로 얻은 문서 목록을 RunnableLambda로 문자열로 바꾸고,
# question 경로는 RunnablePassthrough로 질문을 그대로 전달합니다.
# 두 출력은 각 키를 변수 이름으로 사용하는 프롬프트 템플릿에 전달됩니다.
prompt_chain = {
    "context": retriever | RunnableLambda(format_documents),
    "question": RunnablePassthrough(),
} | prompt

# 체인을 호출할 때 Retriever가 질문을 다시 검색합니다. 이 예제의 마지막 단계는
# 프롬프트 구성까지이며, 생성된 채팅 메시지의 내용을 출력합니다.
prompt_value = prompt_chain.invoke(query)
print("\nLCEL로 만든 프롬프트")
print(prompt_value.to_messages()[0].content)
