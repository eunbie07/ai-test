import cohere
import os
from datetime import datetime

# 1) API 키 불러오기
API_KEY = os.environ.get("CO_API_KEY", "YOUR_API_KEY_HERE")

if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
    raise RuntimeError("CO_API_KEY 환경변수를 먼저 설정해 주세요!")

# 2) 클라이언트 생성 (v2)
co = cohere.ClientV2(API_KEY)

# 3) 실행 시각 (파일명 공통 사용)
now_str = datetime.now().strftime("%Y%m%d_%H%M%S")


def save_to_file_by_model(model_name: str, text: str) -> None:
    """모델별로 결과 파일을 따로 저장하는 함수"""
    # 파일명에 문제될 수 있는 문자 치환
    safe_model_name = model_name.replace("/", "_")
    filename = f"result_{safe_model_name}_{now_str}.txt"

    with open(filename, "a", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"MODEL: {model_name}\n")
        f.write("-" * 60 + "\n")
        f.write(text + "\n\n")

    print(f"저장 완료: {filename}")


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

    # response.message.content 안에서 text 필드만 추출
    parts = []
    for item in response.message.content:
        t = getattr(item, "text", None)
        if t:
            parts.append(t)

    full_text = "\n".join(parts) if parts else "(텍스트 응답 없음)"

    # 콘솔 출력
    print(full_text)
    print()

    # 모델별 파일 저장
    save_to_file_by_model(model_name, full_text)


if __name__ == "__main__":
    # 특허 예시 텍스트 (나중에 실제 청구항 넣어도 됨)
    patent_text = """
    이 발명은 리튬 이온 2차 전지의 수명을 향상시키기 위한 전극 구조에 관한 것이다.
    양극 및 음극 사이에 특수한 세퍼레이터 구조를 도입하여 충방전 사이클 시 용량 저하를 최소화한다.
    """

    # 1) 초저비용 요약/RAG용
    run_model("command-r7b-12-2024", patent_text)

    # 2) 균형형 운영 후보(Command R 업데이트 버전)
    run_model("command-r-08-2024", patent_text)

    # 3) 고성능 일반 생성/보고서용(Command A 최신)
    run_model("command-a-03-2025", patent_text)

    # 4) 고급 추론용(Reasoning)
    run_model("command-a-reasoning-08-2025", patent_text)
