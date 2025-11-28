# Gemini File Search API 테스트 결과

## 결론

- uploadToFileSearchStore API를 통해 파일 업로드 후 AI 호출이 정상 동작함
  - 파일 경로 방식, bytes 변수 방식 모두 성공

- 프롬프트에서 문서를 지칭하는 표현은 어떤 것을 사용해도 동일하게 동작함
  - 테스트한 7가지 표현 모두 성공: "문서", "파일", "자료", "업로드된 문서", "첨부된 파일", "제공된 자료", "참고 문서"

---

## 제한사항

| 항목 | 내용 |
|------|------|
| 최대 파일 크기 | 100MB |

### 지원 파일 형식 (주요)

| 형식 | 확장자 |
|------|--------|
| PDF | .pdf |
| Word | .docx, .doc |
| Excel | .xlsx, .xls |
| PowerPoint | .pptx |
| 텍스트 | .txt |
| CSV | .csv |
| JSON | .json |
| HTML | .html |
| Markdown | .md |
| 한글 | .hwp |

- 전체 지원 형식은 [공식문서](https://ai.google.dev/gemini-api/docs/file-search?hl=ko) 참조

### 저장소 크기 제한 (등급별)

| 등급 | 한도 |
|------|------|
| 무료 | 1GB |
| Tier 1 | 10GB |
| Tier 2 | 100GB |
| Tier 3 | 1TB |

- 권장: 파일 검색 스토어당 20GB 미만 (검색 지연 시간 최적화)
- 실제 저장 크기는 입력 데이터의 약 3배 (임베딩 포함)

### 데이터 보존

- Files API로 업로드된 원본 파일: **48시간 후 삭제**
- 파일 검색 스토어에 가져온 데이터: **수동 삭제 전까지 무기한 저장**

---

## 비용

| 항목 | 비용 |
|------|------|
| 색인 생성 (임베딩) | 토큰 1백만 개당 $0.15 |
| 보관 | 무료 |
| 쿼리 시 임베딩 | 무료 |
| 검색된 문서 토큰 | 일반 컨텍스트 토큰으로 청구 |

---

## 참고 링크

- [File Search 개요](https://ai.google.dev/gemini-api/docs/file-search?hl=ko)

---

# 상세 내용 

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
| 테스트 일자 | 2025-11-28 |

---

## 테스트 결과

### 1. uploadToFileSearchStore API 활용

**결과: 성공**

#### 방식 1: 파일 경로로 업로드 (공식문서 방식)

```python
operation = client.file_search_stores.upload_to_file_search_store(
    file="sample_document.txt",
    file_search_store_name=store_name,
    config={"display_name": "sample_document.txt"}
)
```

#### 방식 2: bytes 변수로 업로드 (워크어라운드)

API가 bytes 직접 업로드를 지원하지 않아, 임시 파일 생성 방식으로 우회:

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

- 공식 문서에는 파일 경로 업로드만 문서화되어 있으며, 본 방식은 테스트를 통해 검증한 워크어라운드임
- 파일 크기 제한: 최대 100MB

- 파일 검색 스토어 생성 후 파일 업로드 가능
- 업로드는 비동기 작업으로, 완료까지 polling 필요 (약 5초 소요)
- 두 방식 모두 동일한 스토어에 문서 추가 가능 (테스트에서 2개 문서 업로드 확인)

---

### 2. 프롬프트에서 문서 참조 방식

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
