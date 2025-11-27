# Google Patents Public Data + AI 연동 테스트 결과 보고

## 결론

> **BigQuery를 통한 Google Patents Public Data 접근 가능 확인**
> **GPT / Gemini / Claude 3개 AI 모두 Tool 연동 및 특허 분석 기능 정상 동작**

---

## 1. 테스트 목적

- AI 호출 시 BigQuery Tool을 통해 Google Patents Public Data 접근 가능 여부 검증
- Gemini / Claude / GPT 적용 가능 여부 검토

---

## 2. 구현 내용

| 구성요소 | 설명 |
|---------|------|
| BigQuery 연동 | `bigquery-public-data.patents.publications` 테이블 쿼리 |
| FastAPI 프록시 | AI가 HTTP로 호출 가능한 Tool API 구현 |
| AI 연동 | GPT, Gemini, Claude 3종 모두 연동 |

### 아키텍처

```
[AI (GPT/Gemini/Claude)]
        ↓ HTTP 호출
[FastAPI 프록시 서버]
        ↓ BigQuery Client
[Google Patents Public Data]
```

---

## 3. 테스트 결과

| 항목 | 결과 | 비고 |
|-----|------|------|
| BigQuery → Google Patents 접근 | O 성공 | gcloud 인증 필요 |
| GPT 연동 | O 성공 | gpt-4.1-mini |
| Gemini 연동 | O 성공 | gemini-2.0-flash |
| Claude 연동 | O 성공 | claude-sonnet-4 |

---

## 4. 각 AI 응답 특징

| AI | 응답 스타일 |
|----|-----------|
| GPT | 개별 특허 상세 분석, 구조적 정리 |
| Gemini | 간결한 요약, 핵심 키워드 중심 |
| Claude | 마크다운 포맷, 카테고리별 분류 |

---

## 5. 필요 환경

```bash
# API Keys
OPENAI_API_KEY=xxx
GEMINI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx

# GCP 인증 (BigQuery 접근용)
gcloud auth application-default login
```

---

## 6. 향후 검토 사항

- 실서비스 적용 시 AI 선택 기준: 응답 스타일 / 비용 / 속도
- 특허 검색 쿼리 고도화 (출원인, 날짜 범위, CPC 코드 등)
- 대량 데이터 처리 시 BigQuery 비용 최적화
