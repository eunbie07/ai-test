# Gemini File Search API 테스트

## 목적 및 결론

- uploadToFileSearchStore API를 통해 파일 업로드 후 AI 호출이 정상 동작함
  - 파일 경로 방식, bytes 변수 방식 모두 성공

- 프롬프트에서 문서를 지칭하는 표현은 어떤 것을 사용해도 동일하게 동작함
  - 테스트한 7가지 표현 모두 성공: "문서", "파일", "자료", "업로드된 문서", "첨부된 파일", "제공된 자료", "참고 문서"

## 사전 준비

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정
```bash
# Windows
set GEMINI_API_KEY=your-api-key-here

# Mac/Linux
export GEMINI_API_KEY=your-api-key-here
```

API 키는 https://aistudio.google.com/apikey 에서 발급

## 실행

```bash
python gemini_file_search_test.py
```

## 테스트 내용

| 테스트 항목 | 설명 |
|------------|------|
| 스토어 생성 | File Search Store 생성 |
| 바이트 업로드 | 파이썬 변수(bytes)로 문서 업로드 |
| 문서 참조 방식 | "문서", "파일", "자료" 등 어떤 표현이 효과적인지 |
| 인용 정보 | grounding_metadata 반환 확인 |

## 파일 구조

```
gemini-file-search/
├── gemini_file_search_test.py  # 메인 테스트 코드
├── sample_document.txt         # 테스트용 샘플 문서
├── requirements.txt            # 의존성
├── README.md                   # 이 파일
├── REPORT.md                   # 테스트 결과 보고서
└── test_result_*.md            # 테스트 실행 결과 (자동 생성)
```
