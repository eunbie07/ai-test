# Gemini File Search API 테스트

## 목적
- `uploadToFileSearchStore` API를 활용한 AI 호출 테스트
- 파이썬 변수를 통한 파일 전달 (UI 없이)
- 프롬프트에서 문서 참조 방식 테스트

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
└── README.md                   # 이 파일
```
