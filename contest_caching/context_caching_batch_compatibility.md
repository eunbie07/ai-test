# Context Caching + Batch API 조합 가능 여부

## 결론 요약

| 서비스 | Batch + Caching 조합 | 최대 할인율 |
|--------|---------------------|-------------|
| **Claude** | O 가능 (best-effort) | 최대 **~95%** |
| **OpenAI** | X 미지원 | Batch만 50% |

---

## Anthropic Claude

### 조합 가능 여부: O 가능

Batch API와 Prompt Caching을 함께 사용할 수 있습니다. 단, **best-effort 방식**으로 캐시 히트가 보장되지는 않습니다.

### 제약 조건

| 항목 | 내용 |
|------|------|
| **최소 토큰 수** | 1,024 토큰 (Haiku 3.5: 2,048 / Haiku 4.5: 4,096) |
| **최대 캐시 크기** | 최대 200K 토큰 (Sonnet 4/4.5는 1M 컨텍스트 윈도우 지원) |
| **캐시 브레이크포인트** | 최대 4개 설정 가능 |
| **지원 모델** | Opus 4/4.1, Sonnet 4/4.5/3.7, Haiku 3/3.5/4.5 |

### 캐싱 유지 시간 (TTL)

| TTL 옵션 | Cache Write 비용 | Cache Read 비용 | 비고 |
|----------|-----------------|-----------------|------|
| **5분 (기본)** | 1.25x (25% 추가) | 0.1x (90% 할인) | 사용 시마다 갱신 |
| **1시간** | 2x (100% 추가) | 0.1x (90% 할인) | Batch 사용 시 권장 |

### 비용

| 유형 | 할인율 |
|------|--------|
| Batch API만 | 50% 할인 |
| Cache Read | 90% 할인 |
| **Batch + Cache Read 조합** | **~95% 할인** |

실제 예시 (Sonnet 3.5, Knowledge Base 시나리오):
- 일반 API: $936.00 → Batch + Caching: **$63.05** (93% 절감)

### 공식 권장 사용법

캐시 히트율을 높이기 위한 **가장 비용 효율적인 방법**:

1. **공유 prefix가 있는 요청들을 모음**
2. **단일 요청으로 캐시 워밍업**: 공유 prefix + 1시간 캐시 블록을 포함한 요청 1개만 먼저 Batch로 전송
3. **첫 번째 작업 완료 모니터링**: 작업 완료 여부 확인
4. **나머지 요청들 제출**: 첫 번째 완료 후 나머지 요청들을 Batch로 전송

**이유**: Batch 요청은 비동기로 동시에 처리되어 순서가 보장되지 않음. 5분 TTL은 Batch 처리 시간(보통 5분~1시간)보다 짧을 수 있어 1시간 TTL 권장.

### 주의사항

- 캐시 히트가 **보장되지 않음** (best-effort)
- 최악의 경우 모든 요청이 Cache Write로 처리되어 오히려 비용 증가 가능

---

## OpenAI GPT

### 조합 가능 여부: X 미지원

Batch API에서는 Prompt Caching 할인이 **적용되지 않습니다**.

### 제약 조건 (일반 API에서의 Caching)

| 항목 | 내용 |
|------|------|
| **최소 토큰 수** | 1,024 토큰 |
| **캐싱 단위** | 첫 1,024 토큰 후 128 토큰씩 증가 |
| **적용 방식** | 자동 (별도 설정 불필요) |
| **지원 모델** | GPT-4o, GPT-4o mini, o1, GPT-4.1 시리즈 |

### 캐싱 유지 시간

| 상황 | 유지 시간 |
|------|----------|
| **일반** | 5~10분 (비활성 시) |
| **최대** | 1시간 (off-peak 시) |
| **수동 설정** | X 불가 |

### 비용

| 유형 | 할인율 |
|------|--------|
| Batch API | 50% 할인 |
| Prompt Caching (일반 API) | 50% (GPT-4o) / 75% (GPT-4.1) |
| **Batch + Caching** | X 조합 불가, Batch 50%만 적용 |

### 커뮤니티 피드백

- "Batch 요청은 Prompt Caching 할인 대상이 아님"
- 많은 개발자들이 Batch + Caching 조합 지원을 요청 중

---

## 비교 요약표

| 항목                  | Claude         | OpenAI       |
| ------------------- | -------------- | ------------ |
| **Batch + Caching** | O 가능           | X 불가         |
| **최대 조합 할인**        | ~95%           | 50% (Batch만) |
| **캐시 최소 토큰**        | 1,024          | 1,024        |
| **캐시 최대 크기**        | 200K (1M 컨텍스트) | 명시 없음        |
| **캐시 TTL**          | 5분/1시간 (선택)    | 5~10분 (자동)   |
| **TTL 수동 설정**       | O 가능           | X 불가         |

---

## Sources

- [Anthropic Prompt Caching 문서](https://docs.claude.com/en/docs/build-with-claude/prompt-caching)
- [Anthropic Prompt Caching 발표](https://www.anthropic.com/news/prompt-caching)
- [Anthropic Batch + Caching 분석](https://llmindset.co.uk/posts/2024/10/anthropic-batch-pricing/)
- [OpenAI Prompt Caching 가이드](https://platform.openai.com/docs/guides/prompt-caching)
- [OpenAI Prompt Caching 발표](https://openai.com/index/api-prompt-caching/)
- [OpenAI 커뮤니티: Batch + Caching 논의](https://community.openai.com/t/can-batch-api-work-with-prompt-caching/1044983)
