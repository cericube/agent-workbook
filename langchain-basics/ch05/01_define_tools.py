# 소스 경로: langchain-basics/ch05/01_define_tools.py
from langchain_core.tools import StructuredTool, tool
from pydantic import BaseModel, Field


# @tool은 함수 이름과 docstring을 도구의 이름과 설명으로 사용합니다.
# 매개변수의 타입 힌트로 입력 스키마를 만듭니다.
@tool
def add(a: int, b: int) -> int:
    """두 정수를 더한 결과를 반환합니다."""
    return a + b


# 도구의 이름과 설명을 출력합니다. invoke에는 인자 이름을 키로 하는 딕셔너리를 전달합니다.
print("=== @Tool 예시 ===")
print(add.name)
print(add.description)
print(add.invoke({"a": 12, "b": 8}))


def multiply_numbers(a: int, b: int) -> int:
    return a * b


# 기존 함수를 감싸면서 도구의 이름과 설명을 직접 지정합니다.
mutiply = StructuredTool.from_function(
    func=multiply_numbers,
    name="multiply ",
    description="두 정수를 곱한 결과를 반환합니다.",
)
print("\n=== StructuredTool 예시 ===")
print(mutiply.name)
print(mutiply.description)
print(mutiply.invoke({"a": 12, "b": 8}))


# 입력 스키마에서 각 인자의 의미와 허용 범위를 선언합니다.
class DivideInput(BaseModel):
    a: float = Field(description="나누어지는 수")
    b: float = Field(gt=0, description="나누는 수")  # 0보다 큰 값만 허용합니다.


# args_schema로 지정한 모델이 invoke 입력을 함수 호출 전에 검증합니다.
@tool(args_schema=DivideInput)
def divide(a: float, b: float) -> float:
    """두 수를 나눈 결과를 반환 합니다."""
    return a / b


print("\n=== @tool(args_schema=DivideInput) 예시 ===")
print(divide.name)
print(divide.description)
print(divide.invoke({"a": 20, "b": 4}))
