# 파일명: cohere_test.py
import cohere
import os

# 1) API 키 설정
#   - 안전하게 하려면, 환경변수 CO_API_KEY에 저장해두고
#   - 코드에서는 os.environ.get(...) 으로 꺼내 쓰는 방식이 좋아.
#   - Cohere docs에서도 CO_API_KEY 환경변수 방식 권장함. 
API_KEY = os.environ.get("CO_API_KEY", "YOUR_API_KEY_HERE")

if API_KEY == "YOUR_API_KEY_HERE":
    raise RuntimeError("Cohere API 키를 먼저 설정해 주세요!")

# 2) 클라이언트 생성 (v2)
co = cohere.ClientV2(API_KEY)


def run_model(model_name: str, text: str) -> None:
    print("=" * 60)
    print(f"MODEL: {model_name}")
    print("-" * 60)

    response = co.chat(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": text,
            }
        ],
    )

    # content 안에 들어있는 아이템 중에서
    # text 속성이 있는 것만 골라서 이어붙이기
    parts = []
    for item in response.message.content:
        # getattr(item, "text", None) 이 있으면 text, 없으면 None
        t = getattr(item, "text", None)
        if t:
            parts.append(t)

    full_text = "\n".join(parts) if parts else "(텍스트 응답 없음)"
    print(full_text)
    print()



if __name__ == "__main__":
    # 특허용 예시 텍스트 (나중에 진짜 청구항으로 바꿔도 됨)
    patent_text = """
    이 발명은 리튬 이온 2차 전지의 수명을 향상시키기 위한 전극 구조에 관한 것이다.
    양극 및 음극 사이에 특수한 세퍼레이터 구조를 도입하여 충방전 사이클 시 용량 저하를 최소화한다.
    """

    # ① 요약/추출형 모델 후보
    run_model("command-r7b-12-2024", patent_text)

    # ② 추론/분석형 모델 후보
    run_model("command-a-reasoning-08-2025", patent_text)
