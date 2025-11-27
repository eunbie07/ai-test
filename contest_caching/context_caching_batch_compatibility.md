# Context Caching + Batch API 조합 가능 여부

## 결론

- **GPT**: Batch에서는 Caching 미지원
- **Claude**: Batch + Caching 조합 가능 (best-effort, 최대 ~95% 할인)
  - 제약 조건: 최소 1,024 토큰 이상, 캐시 브레이크포인트 최대 4개
  - 캐싱 용량: 별도 제한 없음 (컨텍스트 윈도우 내에서 사용)
  - 유지 시간: 5분(기본) / 1시간(최대) 선택 가능
  - 비용: Cache Read 90% 할인, Cache Write 25%~100% 추가

---

## Anthropic Claude

Batch API와 Prompt Caching을 함께 사용할 수 있습니다. 단, **best-effort 방식**으로 캐시 히트가 보장되지는 않습니다.

### 제약 조건

| 항목 | 내용 |
|------|------|
| **최소 토큰 수** | 1,024 토큰 (Haiku 3.5: 2,048 / Haiku 4.5: 4,096) |
| **캐시 브레이크포인트** | 최대 4개 설정 가능 |
| **지원 모델** | Opus 4.5/4.1/4, Sonnet 4.5/4/3.7(deprecated), Haiku 4.5/3.5/3 |

### 캐싱 유지 시간 (TTL)

| TTL 옵션 | Cache Write 비용 | Cache Read 비용 | 비고 |
|----------|-----------------|-----------------|------|
| **5분 (기본)** | 1.25x (25% 추가) | 0.1x (90% 할인) | 사용 시마다 갱신 |
| **1시간 (최대)** | 2x (100% 추가) | 0.1x (90% 할인) | Batch 사용 시 권장 |

### 비용

| 유형 | 할인율 |
|------|--------|
| Batch API만 | 50% 할인 |
| Cache Read | 90% 할인 |
| **Batch + Cache Read 조합** | **~95% 할인** |

### 캐시 히트율 최적화 방법

공식 문서 권장사항:

1. **동일한 cache_control 블록 사용**: 배치 내 모든 요청에 동일한 cache_control 블록 포함
2. **지속적인 요청 스트림 유지**: 캐시 항목이 만료되지 않도록 꾸준한 요청 유지
3. **공유 콘텐츠 최대화**: 요청 간 캐시 가능한 콘텐츠를 최대한 공유하도록 구조화
4. **1시간 TTL 사용 권장**: Batch 처리 시간(최대 24시간)을 고려하여 1시간 캐시 기간 사용

**참고**: Batch 요청은 비동기로 동시에 처리되어 순서가 보장되지 않음. 일반적으로 30%~98%의 캐시 히트율을 경험함.

### 주의사항

- 캐시 히트가 **보장되지 않음** (best-effort)
- 최악의 경우 모든 요청이 Cache Write로 처리되어 오히려 비용 증가 가능

---

## Sources

- [Anthropic Prompt Caching 공식 문서](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Anthropic Batch API 공식 문서](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing)
