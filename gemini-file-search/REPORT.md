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

**참고**: 공식 문서에는 파일 경로 업로드만 문서화되어 있으며, 본 방식은 테스트를 통해 검증한 워크어라운드임

---

### 3. 프롬프트에서 문서 참조 방식

**결과: 모든 표현이 동일하게 작동**

| 표현 | 결과 |
|------|------|
| 문서 | 성공 |
| 파일 | 성공 |
| 자료 | 성공 |
| 업로드된 문서 | 성공 |
| 첨부된 파일 | 성공 |
| 제공된 자료 | 성공 |
| 참고 문서 | 성공 |

**결론**: File Search 도구가 자동으로 스토어에서 관련 내용을 검색하기 때문에, 프롬프트에서 **어떤 단어로 지칭해도 동일하게 동작**함

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

## 제한사항

| 항목 | 내용 |
|------|------|
| 최대 파일 크기 | 100MB |
| 무료 저장소 용량 | 1GB |
| 파이썬 변수(bytes) | 최대 100MB (임시파일 방식이므로 동일 적용) |

---

## 참고 링크

- [File Search 개요](https://ai.google.dev/gemini-api/docs/file-search?hl=ko)
