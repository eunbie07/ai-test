# Google Patents Public Data + AI 연동 테스트 결과 보고

## 결론

- GPT/Gemini/Claude 모두 BigQuery 툴을 직접 호출해 Google Patents Public Data 접근 가능 확인함

- Google Patents 공개 데이터세트 비용 구조
 - 데이터 자체는 별도의 저장 비용 없이 무료로 제공됨
 - BigQuery를 통해 쿼리를 실행할 경우, 스캔되는 데이터 용량 기준으로 비용이 부과됨
 - 매월 1 TiB까지는 무료, 무료 제공량 초과 시, 1 TiB당 약 6.25달러의 비용이 발생함

### 특허 번호 체계

**예시: 엘지지에너지솔루션 리튬이차전지 특허**

| 필드 | Google Patents | KIPRIS |
|------|----------------|--------|
| 공개번호 or 등록번호 (`publication_number`) | `KR-20200023733-A` | `1020200023733` |
| 출원번호 (`application_number`) | `KR-20180100064-A` | `1020180100064` |

**번호 매핑 규칙**: Google Patents 번호에서 `KR-` 접두사와 `-A` 접미사를 제거한 숫자 앞에 `10`을 붙이면 KIPRIS 번호가 됨.


---

## 1. 테스트 목적

- **기술 검증 (PoC)**: AI 에이전트가 BigQuery Tool을 통해 Google Patents Public Data(전세계 특허)에 접근 가능한지 확인
- **모델 호환성**: 주요 LLM (Gemini, Claude, GPT) 모두 적용 가능한지 테스트

---

## 2. 구현 내용

| 구성요소            | 설명                                                                    |
| --------------- | --------------------------------------------------------------------- |
| **BigQuery 연동** | `bigquery-public-data.patents.publications` 테이블 직접 쿼리 (전세계 1억 건+ 데이터) |
| **FastAPI 프록시** | AI가 표준 HTTP 프로토콜로 호출 가능한 Tool API 서버 구축                               |
| **AI 분석 에이전트**  | 검색된 특허 데이터를 바탕으로 기술 트렌드 요약 및 인사이트 도출                                  |

### 아키텍처
```
[User] -> [AI Agent (GPT/Gemini/Claude)] -> [FastAPI Server] -> [BigQuery] -> [Google Patents Data]
```

---

## 3. 테스트 결과

| 항목 | 결과 | 비고 |
|-----|------|------|
| **데이터 접근성** | **성공** | gcloud 인증을 통해 보안 접속 완료 |
| **AI 연동성** | **성공** | 3종 모델 모두 Tool 호출 및 응답 처리 완벽 수행 |
| **GPT 연동** | **성공** | **gpt-5.1** (최신 모델 적용) |
| **Gemini 연동** | **성공** | **gemini-2.5-pro** (고성능 모델 적용) |
| **Claude 연동** | **성공** | **claude-sonnet-4-5** (20250929 버전) |

---

## 4. 비용 분석

Google Patents 공개 데이터세트 비용 구조
- 데이터 자체는 별도의 저장 비용 없이 무료로 제공됨
- BigQuery를 통해 쿼리를 실행할 경우, 스캔되는 데이터 용량 기준으로 비용이 부과됨
- 매월 1 TiB까지는 무료로 제공됨
- 무료 제공량 초과 시, 1 TiB당 약 6.25달러의 비용이 발생함

---

## 부록: 개발 가이드 및 환경 설정

### 필요 환경
```bash
# API Keys
OPENAI_API_KEY=xxx
GEMINI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx

# GCP 인증
gcloud auth application-default login
```


### 주요 데이터 필드

| Field | Type | Description | Note |
|-------|------|-------------|------|
| `publication_number` | STRING | Publication number (Primary Key) | `-A`: 공개, `-B1`: 등록 |
| `application_number` | STRING | Application number | 공개/등록 문서 연결 키 |
| `country_code` | STRING | Country code | US, KR, JP, CN, etc. |
| `title_localized` | RECORD | Title (multilingual) | Keyword search target |
| `abstract_localized` | RECORD | Abstract (multilingual) | All countries |
| `publication_date` | INTEGER | Publication date | YYYYMMDD |
| `filing_date` | INTEGER | Filing date | YYYYMMDD |
| `grant_date` | INTEGER | Grant date | YYYYMMDD |
| `assignee` | STRING | Assignee | REPEATED |
| `inventor` | STRING | Inventor | REPEATED |
| `cpc` | RECORD | CPC classification | REPEATED |
| `ipc` | RECORD | IPC classification | REPEATED |
| `citation` | RECORD | Cited patents | REPEATED |
| `parent` | RECORD | Parent application | REPEATED |
| `child` | RECORD | Child application | REPEATED |
| `family_id` | STRING | Patent family ID | Family search |

> **참고**: BigQuery 공개 데이터셋에서 청구항(`claims_localized`)과 상세설명(`description_localized`)은 **US 특허만** 제공됨

### Google Patents vs KIPRIS 비교

| 항목 | Google Patents (BigQuery) | KIPRIS |
|------|---------------------------|--------|
| **법적 상태** | `entity_status` 필드 있으나 대부분 비어있음 | 실시간 확인 가능 (유지/소멸/포기 등) |
| **등록번호** | 미제공 | 제공 |
| **등록일** | `grant_date` 필드 있으나 비어있는 경우 많음 | 제공 |
| **청구항** | US 특허만 제공 | 한국 특허 전문 제공 |
| **심사/심판 이력** | 미제공 | 제공 |
| **연차료 납부 여부** | 미제공 | 제공 |
| **용도** | 전세계 특허 검색/분석 | 한국 특허 권리 확인 |

> **`entity_status`가 비어있는 이유**: Google Patents BigQuery는 전세계 특허청의 공개 데이터를 수집하지만, 법적 상태(유지/소멸 등)는 각국 특허청에서 실시간으로 관리하는 정보로, BigQuery에 반영되지 않거나 갱신이 늦음. 정확한 권리 상태 확인은 해당 국가 특허청(한국: KIPRIS) 직접 조회 필요.

### 샘플 쿼리 (BigQuery Console)

특정 공개번호로 전체 필드 조회:
```sql
SELECT
  publication_number,
  application_number,
  country_code,
  kind_code,
  application_kind,
  application_number_formatted,
  pct_number,
  family_id,
  spif_publication_number,
  spif_application_number,
  title_localized,
  abstract_localized,
  claims_localized,
  claims_localized_html,
  description_localized,
  description_localized_html,
  publication_date,
  filing_date,
  grant_date,
  priority_date,
  priority_claim,
  inventor,
  inventor_harmonized,
  assignee,
  assignee_harmonized,
  examiner,
  uspc,
  ipc,
  cpc,
  fi,
  fterm,
  locarno,
  citation,
  parent,
  child,
  entity_status,
  art_unit
FROM
  `bigquery-public-data`.`patents`.`publications`
WHERE
  publication_number = 'KR-20200023733-A';
```

---

## 참고자료

- [BigQuery 공개 데이터셋 - patents](https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data)
- [BigQuery 가격 정책](https://cloud.google.com/bigquery/pricing)
- [KIPRIS (한국특허정보검색서비스)](https://www.kipris.or.kr/khome/main.do)