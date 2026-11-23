# 파일명: /ch02/01_prompt_template.py

import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# .env 파일의 설정을 읽되 이미 설정된 환경 변수는 덮어쓰지 않습니다.
load_dotenv()

# 사용할 모델 이름과 API 키를 읽고, 누락되거나 빈 문자열이면 종료합니다.
model_name = os.getenv("GEMINI_MODEL")
api_key = os.getenv("GEMINI_API_KEY")

if not model_name or not api_key:
    raise SystemExit(".env에 GEMINI_MODEL과 GEMINI_API_KEY를 설정해 주세요.")

# 완성된 프롬프트를 Gemini Developer API로 전송할 모델 객체를 만듭니다.
model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api_key,
    vertexai=False,  # Gemini Developer API 사용
)

# 세 가지 템플릿 사용 방식에 동일한 요약 대상 문서를 사용합니다.
document = (
    "파이썬의 리스트와 튜플은 여러 값을 순서대로 저장합니다. "
    "리스트는 생성한 뒤에도 요소를 추가하거나 수정할 수 있습니다. "
    "튜플은 생성한 뒤 요소를 다른 값으로 바꿀 수 없습니다. "
    "내용을 자주 바꾸는 데이터에는 리스트를, "
    "요소 구성을 유지할 데이터에는 튜플을 사용할 수 있습니다."
)

# 중괄호로 표시한 language와 document는 실행 시 채울 입력 변수입니다.
template_text = (
    "다음 문서의 핵심 내용을 {language}로 두 문장으로 요약하세요.\n문서:\n{document}"
)

# 1. from_template()은 템플릿 문자열에서 입력 변수를 자동으로 추출합니다.
print("=== 입력 변수 자동 추출 ===")
template = PromptTemplate.from_template(template_text)
print("입력 변수:", template.input_variables)
# format()은 변수 값을 채운 문자열을 반환하며, 모델을 호출하지 않습니다.
prompt_text = template.format(language="영어", document=document)
print(prompt_text)

# 완성된 문자열을 모델에 전달하는 단계에서 실제 API 요청이 발생합니다.
response = model.invoke(prompt_text)
print("=== 요약 답변 ===")
print(response.text)

# 2. 생성자에 템플릿 문자열과 입력 변수 목록을 직접 지정할 수도 있습니다.
print("\n=== 입력 변수 직접 지정 ===")
explicit_template = PromptTemplate(
    template=template_text,
    input_variables=["language", "document"],
)
print(explicit_template.format(language="한국어", document=document))


# 3. partial()은 일부 변수 값을 미리 채운 새 템플릿을 만듭니다.
# 언어를 한국어로 고정하면 이후에는 요약할 문서만 전달하면 됩니다.
print("\n=== partial(): 일부 변수 미리 지정 ===")
korean_template = template.partial(language="한국어")
print("남은 입력 변수:", korean_template.input_variables)
# 여기서는 프롬프트 문자열만 출력하며 추가 모델 호출은 하지 않습니다.
korean_prompt_text = korean_template.format(document=document)
print(korean_prompt_text)
