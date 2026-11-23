# 소스 경로: langchain-basics/ch04/04_runnable_passthrough.py

from typing import Any

from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)


def calculate_price_with_tax(item: dict[str, Any]) -> int:
    return item["price"] * 110 // 100


def format_price(item: dict[str, Any]) -> str:
    return f"{item['original']['product']}의 세금 포함 가격은 {item['price_with_tax']:,}원입니다."


product = {"product": "키보드", "price": 10_000}

# LCEL에서 A | B로 연결하면 B는 A의 출력을 받습니다.
# 가격 계산 결과인 11000만 넘기면 다음 단계에서 상품명을 읽을 수 없습니다.
print("가격 계산 결과", calculate_price_with_tax(product))

# 같은 상품 정보를 두 갈래에 전달합니다. original에는 원본을 담고,
# RunnableParallel은 입력 하나를 여러 작업에 각각 전달하고,
# 각 작업의 결과를 하나의 딕셔너리로 모으는 LangChain 클래스입니다.
parallel_chain = RunnableParallel(
    original=RunnablePassthrough(),
    price_with_tax=calculate_price_with_tax,
)
print("두 갈래의 결과", parallel_chain.invoke(product))

message_chain = parallel_chain | RunnableLambda(format_price)
print(message_chain.invoke(product))

# assign()은 입력 딕셔너리의 기존 키와 계산한 키를 같은 깊이에 둡니다.
# 계산 함수에는 상품 정보 전체가 전달되고, 반환값은 price_with_tax에 들어갑니다.
tax_chain = RunnablePassthrough.assign(price_with_tax=calculate_price_with_tax)
result = tax_chain.invoke(product)
print("계산 결과를 추가한 상품 정보", result)
print("원본 상품 정보", product)
