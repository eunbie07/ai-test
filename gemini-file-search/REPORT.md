# Gemini File Search API 테스트 보고서

## 최종 결론

| 테스트 항목  | 결과     | 비고                                                |
| ------- | ------ | ------------------------------------------------- |
| API 호출  | **가능** | `uploadToFileSearchStore` API를 통한 프로그래밍 방식 파일 업로드 |
| 변수 전달   | **가능** | 임시 파일 생성 방식으로 파이썬 변수(bytes)를 통한 파일 전달             |
| 프롬프트 표현 | **무관** | 문서/파일/자료 등 어떤 표현을 사용해도 File Search 도구가 자동으로 검색 수행 |

---

## 테스트 목적

1. `uploadToFileSearchStore` API를 활용한 AI 호출 테스트
2. UI를 통한 파일 첨부가 아닌, **파이썬 변수를 통한 파일 전달** 가능 여부 확인
3. 프롬프트에서 업로드된 문서를 어떻게 지칭해야 하는지 확인

---

## 테스트 환경

| 항목 | 내용 |
|------|------|
| 모델 | gemini-2.5-flash |
| SDK | google-genai |
| 테스트 일자 | 2025-11-27 |

---

## 테스트 결과

### 1. uploadToFileSearchStore API 활용

**결과: 성공**

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file=file_path,
    file_search_store_name=store_name,
    config={"display_name": filename, "mime_type": "text/plain"}
)
```

- 파일 검색 스토어 생성 후 파일 업로드 가능
- 업로드는 비동기 작업으로, 완료까지 polling 필요 (약 5초 소요)

---

### 2. 파이썬 변수를 통한 파일 전달

**결과: 성공 (임시 파일 방식)**

API가 bytes 직접 업로드를 지원하지 않아, 다음 방식으로 우회:

```python
# 1. 변수에 문서 내용 정의
test_document_content = """문서 내용...""".encode('utf-8')

# 2. 임시 파일 생성
with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as tmp_file:
    tmp_file.write(content)
    tmp_path = tmp_file.name

# 3. 업로드
operation = client.file_search_stores.upload_to_file_search_store(
    file=tmp_path,
    file_search_store_name=store_name,
    config={"display_name": filename, "mime_type": "text/plain"}
)

# 4. 임시 파일 삭제
os.unlink(tmp_path)
```

---

### 3. 프롬프트에서 문서 참조 방식

**결과: 모든 표현이 동일하게 작동**

| 표현 | 결과 | 비고 |
|------|------|------|
| 문서 | 성공 | |
| 파일 | 성공 | |
| 자료 | 성공 | |
| 업로드된 문서 | 성공 | |
| 첨부된 파일 | 성공 | |
| 제공된 자료 | 성공 | |
| 참고 문서 | 성공 | |

**결론**: File Search 도구가 자동으로 스토어에서 관련 내용을 검색하기 때문에, 프롬프트에서 **어떤 단어로 지칭해도 동일하게 동작**함. 심지어 문서를 명시적으로 언급하지 않아도 검색이 수행됨.

---

## 인용 정보 (grounding_metadata)

File Search 사용 시 응답에 `grounding_metadata`가 포함되어 출처 확인 가능:

```python
# 인용 정보 접근
grounding_metadata = response.candidates[0].grounding_metadata

# 포함 정보
- grounding_chunks: 검색된 문서 청크 (원본 텍스트, 파일명)
- grounding_supports: 응답의 어느 부분이 어떤 청크에서 왔는지
```

예시 출력:
```
grounding_chunks=[GroundingChunk(
  retrieved_context=GroundingChunkRetrievedContext(
    text="# 프로젝트 기술 문서...",
    title='project_docs.md'
  )
)]
```

---

## 핵심 코드 구조

```python
from google import genai
from google.genai import types

# 1. 클라이언트 생성
client = genai.Client(api_key=API_KEY)

# 2. 파일 검색 스토어 생성
store = client.file_search_stores.create(
    config=types.CreateFileSearchStoreConfig(display_name="store-name")
)

# 3. 파일 업로드
operation = client.file_search_stores.upload_to_file_search_store(
    file="document.txt",
    file_search_store_name=store.name,
    config={"display_name": "document.txt"}
)

# 4. 업로드 완료 대기
while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

# 5. File Search로 쿼리
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="질문 내용",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store.name]
                )
            )
        ]
    )
)
```

---

## 제한사항 및 참고사항

| 항목 | 내용 |
|------|------|
| 최대 파일 크기 | 100MB |
| 무료 저장소 용량 | 1GB |
| 권장 스토어 크기 | 20GB 미만 |
| 인덱싱 비용 | 토큰 100만 개당 $0.15 |
| 보관/쿼리 비용 | 무료 (검색된 문서만 컨텍스트 토큰으로 청구) |
| 지원 모델 | gemini-2.5-flash, gemini-2.5-pro, gemini-3-pro-preview 등 |

---

## API 레퍼런스 (공식 문서 기준)

### 주요 API 엔드포인트

### FileSearchStores API
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| `uploadToFileSearchStore` | `POST /v1beta/{fileSearchStoreName}:uploadToFileSearchStore` | 파일을 스토어에 업로드 |
| `fileSearchStores.create` | `POST /v1beta/fileSearchStores` | 빈 스토어 생성 |
| `fileSearchStores.delete` | `DELETE /v1beta/{name}` | 스토어 삭제 |
| `fileSearchStores.get` | `GET /v1beta/{name}` | 스토어 정보 조회 |
| `fileSearchStores.list` | `GET /v1beta/fileSearchStores` | 스토어 목록 조회 |
| `fileSearchStores.importFile` | `POST /v1beta/{fileSearchStoreName}:importFile` | 기존 파일 가져오기 |

### Documents API (문서 관리)
| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| `documents.get` | `GET /v1beta/{name=fileSearchStores/*/documents/*}` | 문서 정보 조회 |
| `documents.list` | `GET /v1beta/{parent=fileSearchStores/*}/documents` | 스토어 내 문서 목록 조회 |
| `documents.delete` | `DELETE /v1beta/{name=fileSearchStores/*/documents/*}` | 문서 삭제 |

### uploadToFileSearchStore 요청 본문

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `displayName` | string | 선택 | 생성된 문서의 표시 이름 |
| `customMetadata` | object[] | 선택 | 데이터와 연결할 맞춤 메타데이터 |
| `chunkingConfig` | object | 선택 | 청크 구성 (미제공 시 기본값 사용) |
| `mimeType` | string | 선택 | 데이터의 MIME 유형 (미제공 시 자동 추론) |

### FileSearchStore 리소스 구조

```json
{
  "name": "fileSearchStores/my-store-123abc",
  "displayName": "My Document Store",
  "createTime": "2025-11-27T10:00:00Z",
  "updateTime": "2025-11-27T10:05:00Z",
  "activeDocumentsCount": "5",
  "pendingDocumentsCount": "0",
  "failedDocumentsCount": "0",
  "sizeBytes": "102400"
}
```

### Document 리소스 구조

```json
{
  "name": "fileSearchStores/my-store-123/documents/my-doc-abc",
  "displayName": "프로젝트 기술문서",
  "customMetadata": [
    {"key": "author", "stringValue": "홍길동"},
    {"key": "year", "numericValue": 2025}
  ],
  "createTime": "2025-11-27T10:00:00Z",
  "updateTime": "2025-11-27T10:05:00Z",
  "state": "STATE_ACTIVE",
  "sizeBytes": "10240",
  "mimeType": "text/plain"
}
```

**Document 상태 (state):**
| 상태 | 설명 |
|------|------|
| `STATE_PENDING` | 처리 중 (임베딩 및 벡터 저장) |
| `STATE_ACTIVE` | 처리 완료, 검색 가능 |
| `STATE_FAILED` | 처리 실패 |

### customMetadata 활용

파일에 메타데이터를 추가하여 나중에 필터링 검색이 가능:

**업로드 시 메타데이터 추가:**
```python
operation = client.file_search_stores.upload_to_file_search_store(
    file=file_path,
    file_search_store_name=store_name,
    config={
        "display_name": "document.txt",
        "custom_metadata": [
            {"key": "author", "string_value": "홍길동"},
            {"key": "department", "string_value": "연구소"},
            {"key": "year", "numeric_value": 2025}
        ]
    }
)
```

**메타데이터 필터링 검색:**
```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="질문 내용",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store_name],
                    metadata_filter="author=홍길동"  # 특정 작성자 문서만 검색
                )
            )
        ]
    )
)
```

### 필터 문법 예시

| 필터 | 설명 |
|------|------|
| `author=홍길동` | author가 "홍길동"인 문서 |
| `year>2024` | year가 2024보다 큰 문서 |
| `department=연구소 AND year=2025` | 복합 조건 |

### 참고 링크

- [File Search 개요](https://ai.google.dev/gemini-api/docs/file-search?hl=ko)
- [File Search Stores API 레퍼런스](https://ai.google.dev/api/rest/v1beta/fileSearchStores)
- [Documents API 레퍼런스](https://ai.google.dev/api/rest/v1beta/fileSearchStores.documents)
