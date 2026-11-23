# 소스 경로: langchain-basics/ch04/05_runnable_parallel.py

from langchain_core.runnables import RunnableLambda, RunnableParallel


def double_number(number: int) -> int:
    return number * 2


def square_number(number: int) -> int:
    return number**2


def triple_number(number: int) -> int:
    return number * 3


# 각 함수를 RunnableLambda로 감싸고 분기 이름을 지정합니다.
# 각 분기의 반환값은 지정한 이름을 키로 하는 딕셔너리에 모입니다.
calculation_chain = RunnableParallel(
    double=RunnableLambda(double_number),
    square=RunnableLambda(square_number),
    triple=RunnableLambda(triple_number),
)

# 세 분기 모두 같은 입력 5를 받아 각각 두 배, 제곱, 세 배를 계산합니다.
# 출력은 {'double': 10, 'square': 25, 'triple': 15}입니다.
print(calculation_chain.invoke(5))


######################################################################
