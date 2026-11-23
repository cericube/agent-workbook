# 소스 경로: langchain-basics/ch04/06_runnable_parallel_llm.py

import os

from dotenv import load_dotenv
from langchain_core.output_parsers import (
    StrOutputParser,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_google_genai import ChatGoogleGenerativeAI

# .env의 설정을 불러와 모델 이름과 API 키를 환경 변수에서 읽을 수 있게 합니다.
load_dotenv()

model: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY"),
)

# 두 프롬프트는 같은 topic을 사용해 각각 개념 설명과 활용 사례를 요청합니다.
description_prompt = ChatPromptTemplate.from_template(
    "{topic}의 개념을 한국어로 직관적인 한 문장으로 설명하세요."
)
example_prompt = ChatPromptTemplate.from_template(
    "{topic}의 활용 사례 1개를  한국어로 간략한 문장으로 설명하세요."
)

parser = StrOutputParser()

# 각 분기는 같은 입력 딕셔너리를 받아 프롬프트를 채우고, 모델 응답에서 텍스트를 추출합니다.
# 두 분기의 결과는 description과 examples를 키로 하는 딕셔너리에 모입니다.
parallel_chain = RunnableParallel(
    description=description_prompt | model | parser,
    examples=example_prompt | model | parser,
)


def format_result(data: dict[str, str]) -> str:
    # 병렬 실행 결과를 제목이 붙은 하나의 문자열로 합칩니다.
    return f"■ 개념 설명\n{data['description']}\n\n■ 활용 사례\n{data['examples']}"


# |로 연결하면 두 분기의 결과 딕셔너리가 format_result에 전달됩니다.
topic_chain = parallel_chain | RunnableLambda(format_result)

# invoke()는 주제 하나를 받아 완성된 결과 하나를 반환합니다.
print("\n=== invoke() ===")
print(topic_chain.invoke({"topic": "LangChain"}))

# batch()는 여러 주제를 받아 입력 순서대로 결과 리스트를 반환합니다.
print("\n=== batch() ===")
topics = [{"topic": "LangChain"}, {"topic": "LCEL"}]
for topic, result in zip(topics, topic_chain.batch(topics), strict=True):
    print(f"\n[{topic['topic']}]")
    print(result)

# format_result는 두 응답이 모두 모일 때까지 기다리므로,
# 분기별 응답 조각을 바로 보려면 parallel_chain에서 stream()을 호출합니다.
print("\n=== stream() ===")
for chunk in parallel_chain.stream({"topic": "LangChain"}):
    # 두 분기의 조각이 섞여 도착할 수 있어 분기 이름도 함께 표시합니다.
    for branch, text in chunk.items():
        if text:
            print(f"[{branch}] {text}", flush=True)
