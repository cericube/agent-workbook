# 소스 경로: langchain-basics/ch03/03_structured_output.py

import os
from datetime import date
from typing import cast

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

load_dotenv()

model_name: str | None = os.getenv("GEMINI_MODEL")
api_key: str | None = os.getenv("GEMINI_API_KEY")

if not model_name or not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")

model: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api_key,
    vertexai=False,  # Gemini Developer API 사용
)


# 회의 메모에서 추출한 할 일 한 건을 나타냅니다. 담당자, 할 일, 마감일을 담습니다.
class ActionItem(BaseModel):
    assignee: str = Field(description="담당자 이름")
    task: str = Field(description="담당자가 수행할 일")
    # 필드는 필수이며, 마감일이 명시되지 않은 항목은 null 값을 허용합니다.
    due_date: date | None = Field(
        description="마감일(YYYY-MM-DD). 메모에 날짜가 없으면 null",
    )


# 회의 메모 한 건에서 추출한 ActionItem 목록을 담습니다.
# 이 클래스를 채팅 모델에 요청하는 구조화 출력의 최상위 스키마로 사용합니다.
class MeetingActions(BaseModel):
    action_items: list[ActionItem] = Field(description="메모에 나온 할 일 목록")


PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "회의 메모에서 담당자가 정해진 할 일을 원문 순서대로 추출하세요. "
            "마감일이 명시되지 않은 항목은 날짜를 추정하지 말고 null로 반환하세요.",
        ),
        ("human", "회의 메모:\n{meeting_notes}"),
    ]
)


def extract_action_items(meeting_notes: str) -> MeetingActions:
    messages = PROMPT.format_messages(meeting_notes=meeting_notes)
    # JSON 스키마를 지원하는 채팅 모델에 지정된 형식으로 응답하도록 요청합니다.
    # 응답은 LangChain에서 Pydantic 모델로 검증합니다.
    structured_llm = model.with_structured_output(MeetingActions, method="json_schema")
    # LangChain의 반환 타입 선언이 포괄적이므로 타입 검사기에 실제 모델 타입을 알려 줍니다.
    return cast(MeetingActions, structured_llm.invoke(messages))


# 마감일이 있는 할 일, 마감일이 없는 할 일, 담당자가 없는 공지를 함께 넣어 추출 기준을 확인합니다.
meeting_notes = (
    "민지는 2026년 11월 24일까지 화면 시안을 공유하기로 했다.\n"
    "준호는 운영 서버의 로그 보관 정책을 검토하기로 했다.\n"
    "다음 회의 일정은 추후 공지한다."
)

result = extract_action_items(meeting_notes)
print(result.model_dump_json(indent=2))
