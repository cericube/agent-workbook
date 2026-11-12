"""5-1. API 호출 없이 async / await와 순차·동시 실행 비교."""

import asyncio
from time import perf_counter


# async def로 정의한 work는 코루틴 함수
async def work(name):
    # 실제 API 통신 대신 비동기 대기로 I/O 작업을 흉내 냅니다.
    await asyncio.sleep(1)
    return f"{name} 완료"


async def main():
    start = perf_counter()
    # work()가 반환한 코루틴을 await로 실행하고, 완료된 뒤 다음 줄로 진행합니다.
    print(await work("A"))
    print(await work("B"))
    print(f"순차 실행: {perf_counter() - start:.2f}초")

    start = perf_counter()
    # gather가 독립적인 작업들을 함께 진행합니다. CPU 병렬 실행을 의미하지 않습니다.
    print(await asyncio.gather(work("A"), work("B")))
    print(f"동시 실행: {perf_counter() - start:.2f}초")


if __name__ == "__main__":
    asyncio.run(main())
