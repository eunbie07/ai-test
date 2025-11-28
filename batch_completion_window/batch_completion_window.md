# Claude / GPT Batch API: 마감 시간에 따른 비용 변화 조사

## 결론: 마감 시간 선택 옵션 없음

---
## 요약

- 마감 시간 설정값에 따른 추가 비용 변화는 현재 기준으로 존재하지 않음
- GPT 현재 마감 시간 옵션값 `completion_window="24h"` 고정으로 지원 (공식문서 참조)
- Claude 현재 마감 시간 옵션값 없음, 최대 24시간 고정으로 지원 
---

## Anthropic Claude (Message Batches API)

| 항목           | 내용                        |
| ------------ | ------------------------- |
| **완료 시간**    | 최대 24시간                   |
| **할인율**      | 표준 API 대비 **50% 할인** (고정) |
| **마감 시간 옵션** | 없음 (24시간 고정)              |

## OpenAI GPT (Batch API)

| 항목           | 내용                                        |
| ------------ | ----------------------------------------- |
| **완료 시간**    | 최대 24시간 (현재 `completion_window="24h"` 고정) |
| **할인율**      | 표준 API 대비 **50% 할인** (고정)                 |
| **마감 시간 옵션** | 없음 (24시간만 지원)                             |


---

## Sources

- [Anthropic Batch Processing 문서](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing)
- [OpenAI Batch API 문서](https://platform.openai.com/docs/guides/batch)

*마지막 확인: 2025년 11월 28일*
