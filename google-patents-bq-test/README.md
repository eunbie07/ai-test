# Google Patents BigQuery + AI 연동 테스트

Google Patents Public Data를 BigQuery를 통해 조회하고, AI 모델(GPT/Gemini/Claude)로 분석하는 프로젝트입니다.

## 프로젝트 구조

```
google-patents-bq-test/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI 프록시 서버
├── bigquery_patents_tool.py # BigQuery 특허 검색 모듈
├── ai_tool_demo.py          # AI 모델 연동 데모
├── requirements.txt         # 의존성 목록
└── REPORT.md               # 테스트 결과 보고서
```

## 아키텍처

```
[User] -> [AI Agent (GPT/Gemini/Claude)] -> [FastAPI Server] -> [BigQuery] -> [Google Patents Data]
```

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 설정

```bash
# GCP 인증 (BigQuery 접근용)
gcloud auth application-default login

# API 키 환경변수 설정
export OPENAI_API_KEY=xxx
export GEMINI_API_KEY=xxx
export ANTHROPIC_API_KEY=xxx
```

### 3. FastAPI 서버 실행

```bash
uvicorn app.main:app --reload
```

### 4. AI 연동 데모 실행

```bash
python ai_tool_demo.py
```

## API 엔드포인트

### 헬스 체크

```
GET /health
```

### 샘플 특허 조회

```
GET /patents/sample?limit=10
```

### 키워드 검색

```
GET /patents/search?keyword=graphite,흑연&limit=20&countries=US,KR
```

| 파라미터 | 필수 | 설명 | 예시 |
|----------|------|------|------|
| `keyword` | O | 검색 키워드 (쉼표로 여러 개 가능) | `graphite,흑연` |
| `limit` | X | 결과 수 제한 (기본값: 20, 최대: 100) | `10` |
| `countries` | X | 국가 코드 (쉼표 구분) | `US,KR,JP,CN` |

## 주요 기능

- **BigQuery 연동**: `bigquery-public-data.patents.publications` 테이블 직접 쿼리 (전세계 1억 건+ 데이터)
- **FastAPI 프록시**: AI가 표준 HTTP 프로토콜로 호출 가능한 Tool API
- **다중 AI 모델 지원**: GPT, Gemini, Claude 모두 연동 가능

## 비용 구조

- 데이터 자체는 무료
- BigQuery 쿼리 실행 시 스캔 데이터 용량 기준 과금
- 매월 1 TiB까지 무료, 초과 시 1 TiB당 약 $6.25

## 참고자료

- [BigQuery 공개 데이터셋 - patents](https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data)
- [BigQuery 가격 정책](https://cloud.google.com/bigquery/pricing)
