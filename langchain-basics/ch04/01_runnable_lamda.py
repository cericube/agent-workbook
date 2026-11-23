# 소스 경로: langchain-basics/ch04/01_runnable_lamda.py

from langchain_core.runnables import RunnableLambda


def double(number: int) -> int:
    return number * 2


# 일반 파이썬 함수 double을 LangChain에서 실행하고 연결할 수 있는 객체로 감쌉니다.
double_number = RunnableLambda(double)

# invoke(5)는 double에 5를 전달합니다. 반환값 10을 출력합니다.
print(double_number.invoke(5))

# |는 앞 단계의 결과를 다음 단계의 입력으로 넘깁니다.
pipe_result = double_number | double_number
# 5를 두 번 연속으로 두 배로 만들어 5 → 10 → 20 순서로 계산합니다.
print(pipe_result.invoke(5))


def add_ten_to_number(number: int) -> int:
    return number + 10


add_ten = RunnableLambda(add_ten_to_number)
to_text = RunnableLambda(lambda number: f"결과: {number}")

# 세 단계를 연결하면 순서대로 실행할 수 있는 RunnableSequence가 만들어집니다.
number_chain = add_ten | double_number | to_text
print(type(number_chain).__name__)
# 입력값 5에 10을 더하고, 그 결과인 15를 두 배로 만든 뒤 "결과: 30"으로 바꿉니다.
print(number_chain.invoke(5))
