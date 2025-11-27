# Cohere 모델 테스트

특허 텍스트 분석을 위한 Cohere 모델 검토 및 벤치마크 테스트

## 파일 구조

```
cohere/
├── README.md                    # 이 파일
├── REPORT.md                    # 최종 검토 보고서
├── cohere_test.py               # 기본 테스트 코드 (원본)
├── cohere_test_v2.py            # 개선된 벤치마크 코드
├── cohere_real_patent_test.py   # 실제 특허 데이터 테스트
└── 프롬프트 연계 특허 데이터 샘플.txt  # 테스트용 특허 데이터
```

## 실행 방법

### 환경 설정
```bash
# API 키 설정
export CO_API_KEY="your-api-key"
```

### 샘플 벤치마크 실행
```bash
python cohere_test_v2.py
```

### 실제 특허 데이터 테스트
```bash
python cohere_real_patent_test.py
```

## 테스트 모델

| 모델 | 용도 | 비용 (Input/Output per 1M) |
|------|------|---------------------------|
| command-r7b-12-2024 | 경량/저비용 | $0.0375 / $0.15 |
| command-r-08-2024 | 균형형 | $0.15 / $0.60 |
| command-a-03-2025 | 고성능 | $2.50 / $10.00 |
| command-a-reasoning-08-2025 | 추론 특화 | $2.50 / $10.00 |

## 결론

상세 내용은 [REPORT.md](REPORT.md) 참고

| 용도 | 추천 모델 |
|------|-----------|
| 대량 처리/분류 | command-r7b-12-2024 |
| 일반 분석 | command-r-08-2024 |
| 고품질 보고서 | command-a-03-2025 |
| 복잡 추론/청구항 | command-a-reasoning-08-2025 |
