# 2편. Gemini API의 System Instruction과 대화 관리

`ch02`부터 API 예제는 Interactions API만 사용합니다. `ch01`과 같이 각 Python 파일을 직접 실행합니다. 공통 모듈 없이 각 파일에 환경 설정, API 호출, 자원 정리를 담았으며 한글 주석으로 실습 흐름을 설명합니다.

## 준비와 실행

Python 3.12, `google-genai==3.0.0`, `python-dotenv`를 기준으로 작성했습니다.

```bash
python -m pip install "google-genai==3.0.0" python-dotenv
```

`ch01`에서 사용한 `.env`를 그대로 사용합니다. `.env`는 이 디렉터리 또는 상위 디렉터리에 두세요.

```dotenv
GEMINI_API_KEY=발급받은_API_키
GEMINI_MODEL=사용할_모델_ID
```

Interactions API를 지원하고 현재 계정에서 호출 가능한 모델을 지정합니다. 실행은 저장소 루트에서 다음과 같이 합니다. 나머지 파일도 파일 이름만 바꿔 실행할 수 있습니다.

```bash
python gemini-sdk-basics/ch02/system_instruction_interactions.py
```

`async_basics.py`는 키·SDK 설치 없이 실행할 수 있습니다. 나머지는 실제 API를 호출하며 사용량에 따라 비용이 발생할 수 있습니다. 오류가 발생하면 메시지와 traceback을 출력하고 실패 상태로 종료합니다.

## 목차별 실습 순서

| 절 | 파일 | 실습 내용 |
| --- | --- | --- |
| 1 | [system_instruction_interactions.py](system_instruction_interactions.py) | 같은 사용자 질문에 역할을 바꿔 응답 비교, 최상위 `system_instruction` |
| 2–3 | [interactions_conversation.py](interactions_conversation.py) | `store=True`, 이전 ID로 멀티턴 연결, 각 턴의 입력·출력 조회, 이전 ID 없이 새 대화 실행 |
| 4 | [interactions_stream.py](interactions_stream.py) | 일반·스트리밍 응답 비교, 생성·텍스트·완료·오류 이벤트 처리 |
| 5 | [async_basics.py](async_basics.py) | API 없이 코루틴, `await`, `gather`, 순차·동시 실행 시간 비교 |
| 5 | [async_interactions.py](async_interactions.py) | 비동기 일반 호출과 이전 ID를 이용한 순차 대화 |
| 5 | [async_interactions_stream.py](async_interactions_stream.py) | 비동기 스트림 생성과 이벤트 순회 |
| 5 | [sync_async_comparison.py](sync_async_comparison.py) | 같은 독립 질문의 동기 순차·비동기 동시 호출과 소요 시간 비교 |

원래 목차의 generateContent·Chat 관련 항목은 개념 비교로 다루고, 실행 코드는 Interactions API로 통일합니다. generateContent는 요청마다 대화 기록을 전달하고, Chat은 SDK가 기록을 관리합니다. Interactions는 서버에 저장한 대화를 이전 ID로 연결합니다.

## 1. System Instruction과 사용자 입력

System Instruction은 모델의 역할·말투·응답 형식 같은 지침이며, 사용자 프롬프트는 이번에 해결할 질문입니다. 지침은 모델의 행동을 유도하며 결과 형식을 절대적으로 보장하지는 않습니다.

Interactions에서는 최상위 `system_instruction`으로 지침을 전달합니다. `previous_interaction_id`는 대화 입력·출력을 연결하며, System Instruction과 생성 설정은 승계하지 않으므로 각 요청에 다시 지정합니다.

## 2–3. 멀티턴 대화와 서버 기록 관리

첫 요청은 `store=True`로 생성하고 응답의 Interaction ID를 보관합니다. 후속 요청은 `previous_interaction_id`에 직전 응답 ID를 넣고 새 질문과 지침을 전달합니다. 매 턴 반환된 ID로 다음 요청을 연결합니다. 예제에서는 각 턴의 ID를 보관한 뒤 `client.interactions.get(id)`로 조회하고, `steps`에 담긴 `user_input`과 `model_output`의 텍스트를 출력합니다. 마지막에는 이전 ID 없이 같은 질문을 보내, 새 대화에는 앞선 문맥이 전달되지 않는 것을 확인합니다.

Interactions는 저장된 ID로 문맥을 찾으므로 전체 기록을 직접 보내지 않아도 됩니다. `store=False`인 응답은 이후 ID 연결에 사용할 수 없습니다. 저장 기록에는 보존 기간이 있으며 ID가 만료되거나 삭제되면 조회·연결이 실패할 수 있습니다. 동기·비동기 대화 예제는 서버에 실습 기록을 저장하며, 조회를 위해 자동 삭제하지 않습니다. 필요하면 해당 ID로 `client.interactions.delete(id)`를 호출할 수 있습니다. ID를 전달하는 방식도 이전 문맥 처리에 대한 토큰 비용을 없애지는 않습니다.

## 4. 일반 응답과 스트리밍

일반 응답은 완성된 결과를 한 번에 받습니다. 스트리밍은 생성 중인 조각을 순서대로 받아 먼저 도착한 텍스트부터 표시합니다. 전체 생성 시간이 반드시 짧아지는 것은 아닙니다. 조각 하나가 토큰 하나를 뜻하지 않으며, 텍스트가 없는 조각도 있습니다. 전체 결과가 필요하면 텍스트를 누적합니다.

`interactions_stream.py`는 같은 질문을 두 번 호출해 표시 방식을 비교하므로 응답 내용은 달라질 수 있습니다. Interactions 예제는 SDK 3.0.0의 `step.delta` 이벤트 중 `delta.type == "text"`만 출력합니다. 이전 SDK의 `content.delta` 예제와 이벤트 이름을 혼용하지 마세요. 완료 상태를 확인하고 서버 오류 이벤트 또는 완료 없는 종료를 실패로 처리합니다.

## 5. 동기와 비동기

동기 호출은 결과를 기다리는 동안 현재 실행 흐름이 대기합니다. 비동기 호출은 `await`로 I/O 완료를 기다리며 다른 코루틴에 실행 기회를 줍니다. `async def` 호출은 코루틴을 만들고, `asyncio.run(main())`이 이벤트 루프에서 실행합니다. `gather`는 독립적인 요청을 동시에 진행할 때 사용하며 CPU 연산을 병렬화하지 않습니다.

비동기 스트리밍은 먼저 `await`로 스트림을 만든 뒤 `async for`로 이벤트를 받습니다. 이전 응답 ID가 필요한 후속 대화는 앞선 호출이 끝나야 하므로 순차적으로 `await`합니다. Python 비동기 호출과 서버 백그라운드 작업(`background=True`)은 별개의 기능입니다. 예제에서는 `async with`로 비동기 연결을 정리합니다. Jupyter처럼 이벤트 루프가 이미 실행 중인 환경에서는 `asyncio.run()` 대신 `await main()`을 사용합니다.

`sync_async_comparison.py`는 같은 두 질문을 동기로 순차 호출한 뒤 비동기 `gather`로 함께 호출합니다. 총 네 번의 API 요청이 발생합니다. 네트워크·서버 상태와 응답 길이에 따라 측정 시간이 달라지므로, 비동기가 항상 빠르다는 결론보다 요청 진행 방식의 차이를 관찰하세요.

## 공식 참고 문서

- [Google Gen AI Python SDK](https://googleapis.github.io/python-genai/): System Instruction, 동기·비동기 호출
- [Interactions API](https://aistudio.google.com/docs/interactions-overview): 서버 상태 관리, 지침 재지정, 저장 정책
- [텍스트 생성과 스트리밍](https://aistudio.google.com/docs/text-generation): 텍스트 생성과 `step.delta` 이벤트

검증 범위: Python 구문, Ruff, 설치된 SDK의 import 및 응답·이벤트 모델을 통한 오프라인 실행 검증. 실제 Gemini API 응답은 별도 실행이 필요합니다.
