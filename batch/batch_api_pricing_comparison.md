# Claude / GPT Batch API 비용 및 마감 시간 설정

## 결론: 마감 시간 선택 옵션 없음

**두 서비스 모두 현재 마감 시간에 따른 비용 변화가 없습니다.** 둘 다 고정된 24시간 윈도우와 50% 할인율만 제공합니다.

---

## Anthropic Claude (Message Batches API)

| 항목 | 내용 |
|------|------|
| **완료 시간** | 최대 24시간 (대부분 1시간 이내 완료) |
| **할인율** | 표준 API 대비 **50% 할인** (고정) |
| **마감 시간 옵션** | 없음 (24시간 고정) |
| **추가 할인** | Prompt Caching과 조합 시 입력 토큰 최대 **95% 할인** 가능 |

---

## OpenAI GPT (Batch API)

| 항목 | 내용 |
|------|------|
| **완료 시간** | 최대 24시간 (`completion_window="24h"` 고정) |
| **할인율** | 표준 API 대비 **50% 할인** (고정) |
| **마감 시간 옵션** | 없음 (24시간만 지원, Azure도 동일) |
| **참고** | 커뮤니티에서 12시간/며칠 등 다양한 옵션 요청이 있지만 미지원 |

---

## 요약

- **마감 시간 설정에 따른 비용 변화**: 현재 **없음**
- 두 서비스 모두 **24시간 윈도우 / 50% 할인**이라는 단일 옵션만 제공
- 더 빠른 처리를 원하면 일반 API 사용 (할인 없음)
- Claude는 Prompt Caching 조합으로 추가 할인 가능

커뮤니티에서는 "16시간 25% 할인", "며칠 대기 75% 할인" 같은 티어별 옵션 요청이 있지만, 아직 두 서비스 모두 구현하지 않았습니다.

---

## Sources

- [Anthropic Batch API 발표](https://www.anthropic.com/news/message-batches-api)
- [Anthropic Batch 95% 할인 분석](https://llmindset.co.uk/posts/2024/10/anthropic-batch-pricing/)
- [OpenAI Batch API FAQ](https://help.openai.com/en/articles/9197833-batch-api-faq)
- [OpenAI Pricing](https://openai.com/api/pricing/)
- [커뮤니티 요청: 다양한 completion_window 옵션](https://community.openai.com/t/need-more-completion-window-options-for-batching-like-12h-or-multiple-days/1361873)
