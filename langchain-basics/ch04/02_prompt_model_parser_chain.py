# 소스 경로: langchain-basics/ch04/02_prompt_model_parser_chain.py

import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_google_genai import ChatGoogleGenerativeAI

# .env의 설정을 환경 변수로 불러온 뒤 모델 이름과 API 키를 읽습니다.
load_dotenv()

model: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL"),
    api_key=os.getenv("GEMINI_API_KEY"),
)

# 시스템 메시지로 답변 형식을 지정하고, 사용자 메시지의 {topic}에 주제를 넣습니다.
prompt: ChatPromptTemplate = ChatPromptTemplate(
    [
        ("system", "개념을 한국어로 한문장으로 간결하게 설명하세요."),
        ("human", "개념: {topic}"),
    ]
)

parser: StrOutputParser = StrOutputParser()

# |로 각 단계를 연결합니다. 모델은 프롬프트를 받아 응답하고, 파서는 응답의 텍스트를 추출합니다.
topic_chain: RunnableSerializable[dict[str, Any], str] = prompt | model | parser

# invoke에 넘긴 딕셔너리의 topic 값으로 프롬프트를 채우고 체인을 실행합니다.
result: str = topic_chain.invoke({"topic": "LangChain"})

print(type(result).__name__)
print(result)
