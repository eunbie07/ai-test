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

# Context Caching + Batch API 조합 가능 여부

## 결론 요약

| 서비스 | Batch + Caching 조합 | 최대 할인율 |
|--------|---------------------|-------------|
| **Claude** | O 가능 (best-effort) | 최대 **~95%** |
| **OpenAI** | X 미지원 | Batch만 50% |

---

## Anthropic Claude: Prompt Caching + Batch API

### 조합 가능 여부: O 가능

Batch API와 Prompt Caching을 함께 사용할 수 있습니다. 단, **best-effort 방식**으로 캐시 히트가 보장되지는 않습니다.

### 할인율 계산

| 유형 | 할인율 |
|------|--------|
| Batch API만 | 50% 할인 |
| Cache Write (5분) | 25% 추가 비용 (1.25x) |
| Cache Write (1시간) | 100% 추가 비용 (2x) |
| Cache Read | **90% 할인** (0.1x) |
| **Batch + Cache Read 조합** | **~95% 할인** |

### 제약 조건

| 항목 | 내용 |
|------|------|
| **최소 토큰 수** | 1,024 토큰 (Haiku 3.5는 2,048) |
| **캐시 유지 시간 (TTL)** | 5분 (기본) 또는 1시간 (선택) |
| **캐시 브레이크포인트** | 최대 4개 설정 가능 |
| **TTL 갱신** | 캐시 사용 시마다 갱신됨 |
| **지원 모델** | Opus 4/4.1, Sonnet 4/4.5/3.7, Haiku 3/3.5/4.5 |

### Batch에서 Caching 사용 시 주의사항

- Batch 요청은 비동기로 처리되어 **캐시 히트가 보장되지 않음**
- Anthropic은 Batch 처리 시 캐시 적용을 **명시적으로 보장하지 않음**
- 5분 TTL은 Batch 처리 시간보다 짧을 수 있으므로 **1시간 TTL 권장**
- 최악의 경우 모든 요청이 Cache Write로 처리되어 오히려 비용 증가 가능

### 구현 방법

Beta 헤더에 두 기능을 모두 포함:
```python
betas: ['prompt-caching-2024-07-31', 'message-batches-2024-09-24']
```

### 실제 비용 예시

Sonnet 3.5 기준, Knowledge Base 시나리오:
- 일반 API: $936.00
- Batch + Caching: **$63.05** (93% 절감)

---

## OpenAI GPT: Prompt Caching + Batch API

### 조합 가능 여부: X 미지원

OpenAI Batch API는 현재 **Prompt Caching 할인이 적용되지 않습니다**.

### 개별 기능 상세

#### Prompt Caching (일반 API만)

| 항목 | 내용 |
|------|------|
| **할인율** | 50% (GPT-4o), 75% (GPT-4.1) |
| **최소 토큰 수** | 1,024 토큰 |
| **캐시 유지 시간** | 5~10분 (최대 1시간) |
| **적용 방식** | 자동 (별도 설정 불필요) |
| **지원 모델** | GPT-4o, GPT-4o mini, o1, GPT-4.1 시리즈 |

#### Batch API

| 항목 | 내용 |
|------|------|
| **할인율** | 50% |
| **Caching 호환** | X 미지원 |
| **완료 시간** | 최대 24시간 |

### 커뮤니티 피드백

- "Batch 요청은 Prompt Caching 할인 대상이 아님"
- "Flex Processing은 캐시 할인 가능하지만, 일반 Batch는 불가"
- 많은 개발자들이 Batch + Caching 조합 지원을 요청 중

---

## 비교 요약표

| 항목 | Claude | OpenAI |
|------|--------|--------|
| **Batch 할인** | 50% | 50% |
| **Caching 할인** | 90% (read) | 50~75% |
| **Batch + Caching** | O 가능 | X 불가 |
| **최대 조합 할인** | ~95% | 50% (Batch만) |
| **캐시 최소 토큰** | 1,024 | 1,024 |
| **캐시 TTL** | 5분/1시간 (선택) | 5~10분 (자동) |
| **TTL 수동 설정** | O 가능 | X 불가 |

---

## 권장 사항

### 대량 처리 + 비용 최적화가 필요한 경우

**Claude 추천**: Batch + 1시간 TTL Caching 조합으로 최대 95% 절감 가능

### 단순 Batch 처리만 필요한 경우

두 서비스 모두 50% 할인으로 동일

### 실시간 처리 + Caching이 필요한 경우

두 서비스 모두 Caching 지원 (OpenAI는 자동, Claude는 수동 설정)

---

## Sources

- [Anthropic Batch API 발표](https://www.anthropic.com/news/message-batches-api)
- [Anthropic Batch 95% 할인 분석](https://llmindset.co.uk/posts/2024/10/anthropic-batch-pricing/)
- [Anthropic Prompt Caching 문서](https://docs.claude.com/en/docs/build-with-claude/prompt-caching)
- [Anthropic Prompt Caching 발표](https://www.anthropic.com/news/prompt-caching)
- [OpenAI Batch API FAQ](https://help.openai.com/en/articles/9197833-batch-api-faq)
- [OpenAI Pricing](https://openai.com/api/pricing/)
- [OpenAI Prompt Caching 발표](https://openai.com/index/api-prompt-caching/)
- [OpenAI 커뮤니티: Batch + Caching 호환 논의](https://community.openai.com/t/can-batch-api-work-with-prompt-caching/1044983)
- [커뮤니티 요청: 다양한 completion_window 옵션](https://community.openai.com/t/need-more-completion-window-options-for-batching-like-12h-or-multiple-days/1361873)
