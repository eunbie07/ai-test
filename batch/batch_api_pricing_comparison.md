# Claude / GPT Batch API 비용 및 마감 시간 설정

## 결론: 마감 시간 선택 옵션 없음

**두 서비스 모두 현재 마감 시간에 따른 비용 변화가 없습니다.** 둘 다 Batch API 사용시 고정된 최대 24시간과 50% 할인율만 제공합니다.

---

## Anthropic Claude (Message Batches API)

| 항목 | 내용 |
|------|------|
| **완료 시간** | 최대 24시간  |
| **할인율** | 표준 API 대비 **50% 할인** (고정) |
| **마감 시간 옵션** | 없음 (24시간 고정) |
| **배치 제한** | 최대 100,000개 요청 또는 256MB |
| **결과 보존** | 생성 후 29일간 다운로드 가능 |
| **추가 할인** | Prompt Caching과 조합 시 **캐시 히트된 입력 토큰에 한해** 추가 할인 가능 (캐시 적중률: 일반적으로 30%~98%) |

---

## OpenAI GPT (Batch API)

| 항목 | 내용 |
|------|------|
| **완료 시간** | 최대 24시간 (현재 `completion_window="24h"` 고정) |
| **할인율** | 표준 API 대비 **50% 할인** (고정) |
| **마감 시간 옵션** | 없음 (24시간만 지원, Azure도 동일) |
| **배치 제한** | 최대 50,000개 요청 또는 200MB |
| **지원 엔드포인트** | `/v1/responses`, `/v1/chat/completions`, `/v1/embeddings`, `/v1/completions`, `/v1/moderations` |
| **참고** | 커뮤니티에서 12시간/며칠 등 다양한 옵션 요청이 있지만 미지원 |

---

## 요약

- **마감 시간 설정에 따른 비용 변화**: 현재 **없음**
- 두 서비스 모두 **24시간 윈도우 / 50% 할인**이라는 단일 옵션만 제공
- 더 빠른 처리를 원하면 일반 API 사용 (할인 없음)
- Claude는 Prompt Caching 조합으로 캐시 히트된 입력 토큰에 추가 할인 가능



---

## Sources

- [Anthropic Message Batches API 문서](https://docs.anthropic.com/en/docs/build-with-claude/message-batches)
- [Anthropic Batch API 발표](https://www.claude.com/blog/message-batches-api)
- [OpenAI Batch API 문서](https://platform.openai.com/docs/guides/batch)
- [OpenAI Batch API FAQ](https://help.openai.com/en/articles/9197833-batch-api-faq)
- [Azure OpenAI Batch 문서](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/batch)
- [커뮤니티 요청: 다양한 completion_window 옵션](https://community.openai.com/t/need-more-completion-window-options-for-batching-like-12h-or-multiple-days/1361873)

*마지막 확인: 2025년 11월*
