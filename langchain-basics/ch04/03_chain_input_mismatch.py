# 소스 경로: langchain-basics/ch04/03_chain_input_mismatch.py

from langchain_core.runnables import RunnableLambda


# 첫 단계에서 같은 주제를 세 가지 형태로 반환해 뒤 단계의 동작을 비교합니다.
def return_text(topic: str) -> str:
    return topic


def return_wrong_key(topic: str) -> dict[str, str]:
    return {"subject": topic}


def return_topic_dict(topic: str) -> dict[str, str]:
    return {"topic": topic}


def read_topic(value: object) -> str:
    # 앞 단계의 결과를 받으면 자료형을 먼저 확인하고 필요한 키를 읽습니다.
    # 문자열이 들어오면 여기서 TypeError를 발생시킵니다.
    if not isinstance(value, dict):
        raise TypeError(
            f"딕셔너리가 필요합니다. 받은 자료형은 {type(value).__name__}입니다."
        )
    # 딕셔너리에 "topic" 키가 없으면 이 조회에서 KeyError가 발생합니다.
    return value["topic"]


def format_topic(topic: str) -> str:
    # 이 메시지로 앞 단계에서 주제를 꺼내 마지막 단계까지 전달했는지 확인합니다.
    print("마지막 단계가 실행됐습니다.")
    return f"주제: {topic}"


for label, prepare_input in [
    ("문자열을 반환하는 경우", return_text),
    ("topic 키가 없는 딕셔너리를 반환하는 경우", return_wrong_key),
    ("topic 키가 있는 딕셔너리를 반환하는 경우", return_topic_dict),
]:
    print(f"\n[{label}]")

    # |로 체인을 연결할 때는 각 단계의 함수에 실제 값이 전달되지 않습니다.
    chain = (
        RunnableLambda(prepare_input)
        | RunnableLambda(read_topic)
        | RunnableLambda(format_topic)
    )
    print("체인 연결 완료")

    # invoke()로 전달된 값이 read_topic에서 예외를 일으키면 format_topic은 실행되지 않습니다.
    try:
        # 같은 입력으로 시작해 첫 단계의 반환 형태에 따른 차이를 확인합니다.
        print(chain.invoke("LangChain"))
    except (TypeError, KeyError) as error:
        # 예외를 출력하고 다음 예시를 계속 실행합니다.
        print(f"{type(error).__name__}: {error}")
