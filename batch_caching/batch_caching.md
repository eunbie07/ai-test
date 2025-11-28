# Context Caching + Batch API 조합 가능 여부

#### 결론:  GPT Batch에서 Caching 미지원 / 
#### **Claude**: Batch + Caching 조합 가능 (best-effort, 캐시 유지: 5분~1시간)

---

## 요약

- GPT: Batch에서는 Caching 미지원

- Claude: Batch + Caching 조합 가능하지만 최대 1시간
  - 유지 시간: 5분(기본) / 1시간(선택)
  - 비용: 5분 - 기본의 1.25배, 1시간 - 기본의 2배 
  - 비용 예시
   - Batch만: 0.5배 (기존대비 50% 할인)
   - Batch + Cache Write 5분: 0.5 × 1.25 = 0.625배 (기존대비 37.5% 할인)
   - Batch + Cache Write 1시간: 0.5 × 2 = 1배 (할인 없음)
   - Batch + Cache Read: 0.5 × 0.1 = 0.05배 (기존대비 95% 할인)
  - 제약 조건: 최소 1,024~4,096 토큰 이상(모델별 상이), 캐시 브레이크포인트 최대 4개
  - 캐싱 용량: 별도 제한 없음 (컨텍스트 윈도우 내에서 사용)


---

## 1. 조합 가능 여부

| 플랫폼 | Batch + Caching | 비고 |
|--------|-----------------|------|
| **Claude** | O (가능) | best-effort 방식, 캐시 히트 보장 안 됨 |
| **GPT** | X (불가) | Batch API와 Caching 호환 안 됨 |

---

## 2. Claude: Batch + Caching 상세

### 제약 조건

| 항목 | 내용 |
|------|------|
| 최소 캐시 토큰 수 | 모델별 상이 (1,024 ~ 4,096 토큰) |
| 최대 캐시 브레이크포인트 | 4개 |
| 캐시 유지 시간 (TTL) | 5분(기본) / 1시간(추가 비용) |
| 캐시 용량 제한 | 명시된 상한 없음 (토큰 단위로 과금) |

### 모델별 최소 캐시 토큰 수

| 모델 | 최소 토큰 수 |
|------|-------------|
| Claude Opus 4.5, Haiku 4.5 | 4,096 토큰 |
| Claude Sonnet 4.5/4, Opus 4.1/4 | 1,024 토큰 |
| Claude Haiku 3.5/3 | 2,048 토큰 |

### 비용 구조 (Input 토큰 기준, Base 대비)

| 유형 | 비용 배수 | 설명 |
|------|----------|------|
| Batch API | 0.5배 | 50% 할인 (Input, Output 모두 적용) |
| Cache Write (5분 TTL) | 1.25배 | 25% 추가 비용 |
| Cache Write (1시간 TTL) | 2배 | 100% 추가 비용 |
| Cache Read (히트) | 0.1배 | 90% 할인 |
| Cache Refresh (갱신) | 무료 | 캐시 사용 시 자동 갱신 |

### 모델별 가격표 (MTok = 백만 토큰, Input 기준)

| Model | Base Input | 5m Cache Write | 1h Cache Write | Cache Read | Output |
|-------|------------|----------------|----------------|------------|--------|
| Claude Sonnet 4.5 | $3 | $3.75 | $6 | $0.30 | $15 |
| Claude Sonnet 4 | $3 | $3.75 | $6 | $0.30 | $15 |
| Claude Opus 4.5 | $5 | $6.25 | $10 | $0.50 | $25 |
| Claude Opus 4.1 | $15 | $18.75 | $30 | $1.50 | $75 |
| Claude Haiku 4.5 | $1 | $1.25 | $2 | $0.10 | $5 |
| Claude Haiku 3.5 | $0.80 | $1 | $1.6 | $0.08 | $4 |

### Batch + Caching 조합 Input 비용 비교 (Claude Sonnet 4.5 기준)

| 상황                        | 계산식 | 배수 | Input 비용/MTok | 절감률 |
| ------------------------- | ----- | ---- | ------------- | -------------- |
| 일반 요청                     | - | 1배 | $3            | 기준             |
| Batch만                    | 0.5 | 0.5배 | $1.5          | 50%            |
| Batch + Cache Read        | 0.5 × 0.1 | 0.05배 | $0.15         | 95%            |
| Batch + Cache Write (5분)  | 0.5 × 1.25 | 0.625배 | $1.875        | 37.5%          |
| Batch + Cache Write (1시간) | 0.5 × 2 | 1배 | $3            | 0%             |


### Batch에서 캐시 히트율 높이는 방법

Batch 요청은 비동기로 처리되어 순서가 보장되지 않으므로, 캐시 히트는 best-effort 방식으로 제공됨.

**권장 방법 (공식 문서):**
1. 공유 프리픽스가 있는 요청 중 **1건만 먼저** 제출하여 캐시 생성
2. 해당 요청 완료 후 나머지 요청 제출
3. **1시간 TTL 사용 권장** (Batch 처리가 5분~1시간 소요되므로 5분 TTL은 만료 위험)

---

## 3. GPT: Batch에서 Caching 미지원

OpenAI의 Batch API는 Automatic Caching과 호환되지 않습니다.

> "Caching is not compatible with the Batch API."
> — [OpenAI Prompt Caching 공식 문서](https://platform.openai.com/docs/guides/prompt-caching)

- Batch API 사용 시 50% 할인만 적용 (Input, Output 모두)
- 추가 캐싱 할인 불가

---

## 4. 적용 시 고려사항

| 고려사항 | 내용 |
|----------|------|
| 캐시 유지 시간 | 최대 1시간이므로 장기 재활용에는 부적합 |
| 캐시 히트 보장 | best-effort 방식으로 보장되지 않음 |
| 비용 리스크 | Cache Write 시 오히려 비용 증가 가능 (특히 1시간 TTL) |
| 장기 재활용 필요 시 | 분석 결과를 별도 DB에 저장하는 방식이 현실적 |

---

## Sources

- [Anthropic Prompt Caching 공식 문서](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Anthropic Batch API 공식 문서](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing)
- [OpenAI Prompt Caching 공식 문서](https://platform.openai.com/docs/guides/prompt-caching)
