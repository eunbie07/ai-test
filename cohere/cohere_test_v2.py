import cohere
import os
import time
from datetime import datetime

# 1) API 키 불러오기
API_KEY = os.environ.get("CO_API_KEY", "YOUR_API_KEY_HERE")

if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
    raise RuntimeError("CO_API_KEY 환경변수를 먼저 설정해 주세요!")

# 2) 클라이언트 생성 (v2)
co = cohere.ClientV2(API_KEY)

# 3) 실행 시각 (파일명 공통 사용)
now_str = datetime.now().strftime("%Y%m%d_%H%M%S")

# 4) 모델별 비용 정보 (USD per 1M tokens)
MODEL_PRICING = {
    "command-a-03-2025": {"input": 2.50, "output": 10.00},
    "command-a-reasoning-08-2025": {"input": 2.50, "output": 10.00},
    "command-a-vision-07-2025": {"input": 2.50, "output": 10.00},
    "command-a-translate-08-2025": {"input": 2.50, "output": 10.00},
    "command-r-08-2024": {"input": 0.15, "output": 0.60},
    "command-r-plus-08-2024": {"input": 0.15, "output": 0.60},
    "command-r7b-12-2024": {"input": 0.0375, "output": 0.15},
}

# 5) 모델별 스펙 정보
MODEL_SPECS = {
    "command-a-03-2025": {"context": "256K", "max_output": "8K"},
    "command-a-reasoning-08-2025": {"context": "256K", "max_output": "32K"},
    "command-a-vision-07-2025": {"context": "128K", "max_output": "8K"},
    "command-a-translate-08-2025": {"context": "8K", "max_output": "8K"},
    "command-r-08-2024": {"context": "128K", "max_output": "4K"},
    "command-r-plus-08-2024": {"context": "128K", "max_output": "4K"},
    "command-r7b-12-2024": {"context": "128K", "max_output": "4K"},
}


def calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> dict:
    """토큰 수를 기반으로 비용 계산"""
    pricing = MODEL_PRICING.get(model_name, {"input": 0, "output": 0})

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "input_price_per_1m": pricing["input"],
        "output_price_per_1m": pricing["output"],
    }


def run_model(model_name: str, prompt: str, system_prompt: str = None) -> dict:
    """모델 실행 및 성능 측정"""
    print("=" * 70)
    print(f"MODEL: {model_name}")
    print("-" * 70)

    # 메시지 구성
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # 시간 측정 시작
    start_time = time.time()

    # API 호출
    response = co.chat(
        model=model_name,
        messages=messages,
    )

    # 시간 측정 종료
    end_time = time.time()
    latency = end_time - start_time

    # 응답 텍스트 추출
    parts = []
    for item in response.message.content:
        t = getattr(item, "text", None)
        if t:
            parts.append(t)
    full_text = "\n".join(parts) if parts else "(텍스트 응답 없음)"

    # 토큰 사용량 추출
    usage = response.usage
    input_tokens = getattr(usage, "billed_units", None)
    if input_tokens:
        input_tokens = getattr(input_tokens, "input_tokens", 0)
        output_tokens = getattr(response.usage.billed_units, "output_tokens", 0)
    else:
        input_tokens = 0
        output_tokens = 0

    # 비용 계산
    cost_info = calculate_cost(model_name, input_tokens, output_tokens)

    # 결과 정리
    result = {
        "model": model_name,
        "specs": MODEL_SPECS.get(model_name, {}),
        "latency_sec": round(latency, 2),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost_info,
        "response": full_text,
    }

    # 콘솔 출력
    print(f"응답 시간: {result['latency_sec']}초")
    print(f"입력 토큰: {input_tokens:,} | 출력 토큰: {output_tokens:,} | 총: {input_tokens + output_tokens:,}")
    print(f"비용: ${cost_info['total_cost']:.6f} (입력: ${cost_info['input_cost']:.6f}, 출력: ${cost_info['output_cost']:.6f})")
    print("-" * 70)
    print(f"응답:\n{full_text[:500]}{'...' if len(full_text) > 500 else ''}")
    print()

    return result


def save_results(results: list, filename: str = None) -> None:
    """결과를 마크다운 파일로 저장"""
    if not filename:
        filename = f"cohere_benchmark_{now_str}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# COHERE 모델 벤치마크 결과\n\n")
        f.write(f"**실행 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        # 요약 테이블
        f.write("## 성능 요약\n\n")
        f.write("| 모델 | 응답시간 | 입력 토큰 | 출력 토큰 | 비용($) |\n")
        f.write("|------|----------|-----------|-----------|----------|\n")

        for r in results:
            f.write(f"| {r['model']} | {r['latency_sec']:.2f}s | {r['input_tokens']:,} | {r['output_tokens']:,} | ${r['cost']['total_cost']:.6f} |\n")

        f.write("\n---\n\n")

        # 상세 결과
        f.write("## 상세 결과\n\n")
        for r in results:
            f.write(f"### {r['model']}\n\n")
            f.write(f"- **스펙**: Context {r['specs'].get('context', 'N/A')}, Max Output {r['specs'].get('max_output', 'N/A')}\n")
            f.write(f"- **응답 시간**: {r['latency_sec']}초\n")
            f.write(f"- **토큰**: 입력 {r['input_tokens']:,} / 출력 {r['output_tokens']:,}\n")
            f.write(f"- **비용**: ${r['cost']['total_cost']:.6f}\n\n")
            f.write(f"**응답:**\n\n{r['response']}\n\n---\n\n")

    print(f"\n결과 저장 완료: {filename}")


def run_benchmark(prompt: str, system_prompt: str = None, models: list = None) -> list:
    """여러 모델에 대해 벤치마크 실행"""
    if models is None:
        models = [
            "command-r7b-12-2024",
            "command-r-08-2024",
            "command-a-03-2025",
            "command-a-reasoning-08-2025",
        ]

    results = []
    for model in models:
        try:
            result = run_model(model, prompt, system_prompt)
            results.append(result)
        except Exception as e:
            print(f"[ERROR] {model}: {e}\n")
            results.append({
                "model": model,
                "error": str(e),
            })

    return results


if __name__ == "__main__":
    # 특허 예시 텍스트
    patent_text = """
    이 발명은 리튬 이온 2차 전지의 수명을 향상시키기 위한 전극 구조에 관한 것이다.
    양극 및 음극 사이에 특수한 세퍼레이터 구조를 도입하여 충방전 사이클 시 용량 저하를 최소화한다.
    """

    # 시스템 프롬프트 (선택)
    system_prompt = "당신은 특허 분석 전문가입니다. 기술적 내용을 정확하게 분석해주세요."

    # 사용자 프롬프트
    user_prompt = f"""다음 특허 텍스트를 분석하고 요약해주세요:

{patent_text}

다음 항목을 포함해주세요:
1. 핵심 기술 요약 (2-3문장)
2. 주요 구성요소
3. 기술적 효과
"""

    # 벤치마크 실행
    print("\n" + "=" * 70)
    print("COHERE 모델 벤치마크 시작")
    print("=" * 70 + "\n")

    results = run_benchmark(user_prompt, system_prompt)

    # 결과 저장
    save_results(results)

    # 최종 비용 합계
    total_cost = sum(r.get("cost", {}).get("total_cost", 0) for r in results if "cost" in r)
    print(f"\n총 테스트 비용: ${total_cost:.6f}")
