"""
실제 특허 데이터를 활용한 Cohere 모델 벤치마크 테스트
- 프롬프트 연계 특허 데이터 샘플.txt 사용
"""

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

# 3) 실행 시각
now_str = datetime.now().strftime("%Y%m%d_%H%M%S")

# 4) 모델별 비용 정보 (USD per 1M tokens)
MODEL_PRICING = {
    "command-a-03-2025": {"input": 2.50, "output": 10.00},
    "command-a-reasoning-08-2025": {"input": 2.50, "output": 10.00},
    "command-r-08-2024": {"input": 0.15, "output": 0.60},
    "command-r7b-12-2024": {"input": 0.0375, "output": 0.15},
}

# 5) 모델별 스펙 정보
MODEL_SPECS = {
    "command-a-03-2025": {"context": "256K", "max_output": "8K"},
    "command-a-reasoning-08-2025": {"context": "256K", "max_output": "32K"},
    "command-r-08-2024": {"context": "128K", "max_output": "4K"},
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
    }


def run_model(model_name: str, prompt: str, system_prompt: str = None) -> dict:
    """모델 실행 및 성능 측정"""
    print("=" * 70)
    print(f"MODEL: {model_name}")
    print("-" * 70)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    start_time = time.time()

    response = co.chat(
        model=model_name,
        messages=messages,
    )

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

    cost_info = calculate_cost(model_name, input_tokens, output_tokens)

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

    print(f"응답 시간: {result['latency_sec']}초")
    print(f"입력 토큰: {input_tokens:,} | 출력 토큰: {output_tokens:,} | 총: {input_tokens + output_tokens:,}")
    print(f"비용: ${cost_info['total_cost']:.6f}")
    print("-" * 70)
    print(f"응답 (앞 500자):\n{full_text[:500]}...")
    print()

    return result


def save_combined_results(
    claim_results: list,
    summary_results: list,
    claim_info: dict,
    abstract_info: dict,
    patent_title: str
) -> str:
    """청구항 분석과 요약 분석 결과를 하나의 마크다운 파일로 저장"""
    filename = f"real_patent_benchmark_{now_str}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 실제 특허 데이터 벤치마크 결과\n\n")
        f.write(f"**실행 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**테스트 특허**: {patent_title[:50]}...\n\n")
        f.write("---\n\n")

        # ==========================================
        # 1. 테스트 1: 청구항 분석
        # ==========================================
        f.write("## 테스트 1: 청구항 분석\n\n")

        # 테스트 데이터 정보
        f.write("### 입력 데이터 정보\n\n")
        f.write("| 항목 | 값 |\n")
        f.write("|------|----|\n")
        f.write(f"| 입력 텍스트 글자수 | {claim_info['char_count']:,}자 |\n")
        f.write(f"| 추정 토큰수 (글자/3) | ~{claim_info['estimated_tokens']:,} 토큰 |\n")
        f.write(f"| 컨텍스트 사용률 (128K 기준) | {claim_info['context_usage']:.2f}% |\n")
        f.write("\n")

        # 성능 요약 테이블
        f.write("### 성능 요약\n\n")
        f.write("| 모델 | 응답시간 | 입력 토큰 | 출력 토큰 | 비용($) |\n")
        f.write("|------|----------|-----------|-----------|----------|\n")
        for r in claim_results:
            if "error" in r:
                f.write(f"| {r['model']} | ERROR | - | - | {r['error']} |\n")
            else:
                f.write(f"| {r['model']} | {r['latency_sec']:.2f}s | {r['input_tokens']:,} | {r['output_tokens']:,} | ${r['cost']['total_cost']:.6f} |\n")
        f.write("\n")

        # 상세 결과
        f.write("### 상세 응답\n\n")
        for r in claim_results:
            f.write(f"#### {r['model']}\n\n")
            if "error" in r:
                f.write(f"**에러**: {r['error']}\n\n")
            else:
                f.write(f"- **스펙**: Context {r['specs'].get('context', 'N/A')}, Max Output {r['specs'].get('max_output', 'N/A')}\n")
                f.write(f"- **응답 시간**: {r['latency_sec']}초\n")
                f.write(f"- **토큰**: 입력 {r['input_tokens']:,} / 출력 {r['output_tokens']:,}\n")
                f.write(f"- **비용**: ${r['cost']['total_cost']:.6f}\n\n")
                f.write(f"**응답:**\n\n{r['response']}\n\n")

        f.write("---\n\n")

        # ==========================================
        # 2. 테스트 2: 요약 분석
        # ==========================================
        f.write("## 테스트 2: 요약 분석\n\n")

        # 테스트 데이터 정보
        f.write("### 입력 데이터 정보\n\n")
        f.write("| 항목 | 값 |\n")
        f.write("|------|----|\n")
        f.write(f"| 입력 텍스트 글자수 | {abstract_info['char_count']:,}자 |\n")
        f.write(f"| 추정 토큰수 (글자/3) | ~{abstract_info['estimated_tokens']:,} 토큰 |\n")
        f.write(f"| 컨텍스트 사용률 (128K 기준) | {abstract_info['context_usage']:.2f}% |\n")
        f.write("\n")

        # 성능 요약 테이블
        f.write("### 성능 요약\n\n")
        f.write("| 모델 | 응답시간 | 입력 토큰 | 출력 토큰 | 비용($) |\n")
        f.write("|------|----------|-----------|-----------|----------|\n")
        for r in summary_results:
            if "error" in r:
                f.write(f"| {r['model']} | ERROR | - | - | {r['error']} |\n")
            else:
                f.write(f"| {r['model']} | {r['latency_sec']:.2f}s | {r['input_tokens']:,} | {r['output_tokens']:,} | ${r['cost']['total_cost']:.6f} |\n")
        f.write("\n")

        # 상세 결과
        f.write("### 상세 응답\n\n")
        for r in summary_results:
            f.write(f"#### {r['model']}\n\n")
            if "error" in r:
                f.write(f"**에러**: {r['error']}\n\n")
            else:
                f.write(f"- **스펙**: Context {r['specs'].get('context', 'N/A')}, Max Output {r['specs'].get('max_output', 'N/A')}\n")
                f.write(f"- **응답 시간**: {r['latency_sec']}초\n")
                f.write(f"- **토큰**: 입력 {r['input_tokens']:,} / 출력 {r['output_tokens']:,}\n")
                f.write(f"- **비용**: ${r['cost']['total_cost']:.6f}\n\n")
                f.write(f"**응답:**\n\n{r['response']}\n\n")

        f.write("---\n\n")

        # ==========================================
        # 3. 총 비용 요약
        # ==========================================
        f.write("## 총 비용 요약\n\n")
        all_results = claim_results + summary_results
        total_cost = sum(r.get("cost", {}).get("total_cost", 0) for r in all_results if "cost" in r)
        total_input = sum(r.get("input_tokens", 0) for r in all_results if "input_tokens" in r)
        total_output = sum(r.get("output_tokens", 0) for r in all_results if "output_tokens" in r)

        f.write("| 항목 | 값 |\n")
        f.write("|------|----|\n")
        f.write(f"| 총 입력 토큰 | {total_input:,} |\n")
        f.write(f"| 총 출력 토큰 | {total_output:,} |\n")
        f.write(f"| **총 테스트 비용** | **${total_cost:.6f}** |\n")

    print(f"\n결과 저장 완료: {filename}")
    return filename


def load_patent_data(filepath: str) -> dict:
    """특허 데이터 파일에서 각 섹션 추출"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 각 섹션 추출
    sections = {}

    # 발명의명칭 추출
    if "발명의명칭(ORIGINAL):" in content:
        start = content.find("발명의명칭(ORIGINAL):") + len("발명의명칭(ORIGINAL):")
        end = content.find("* **요약")
        sections["title"] = content[start:end].strip().strip('"')

    # 요약 추출
    if "요약(ORIGINAL):" in content:
        start = content.find("요약(ORIGINAL):") + len("요약(ORIGINAL):")
        end = content.find("* **대표청구항")
        sections["abstract"] = content[start:end].strip().strip('"')

    # 대표청구항 추출
    if "대표청구항(ORIGINAL):" in content:
        start = content.find("대표청구항(ORIGINAL):") + len("대표청구항(ORIGINAL):")
        end = content.find("* **상세설명")
        sections["claim"] = content[start:end].strip().strip('"')

    return sections


if __name__ == "__main__":
    # 특허 데이터 로드
    patent_file = "프롬프트 연계 특허 데이터 샘플.txt"

    print("\n" + "=" * 70)
    print("실제 특허 데이터 벤치마크 테스트")
    print("=" * 70)

    try:
        patent_data = load_patent_data(patent_file)
        print(f"\n특허 제목: {patent_data.get('title', 'N/A')[:50]}...")
        print(f"요약 길이: {len(patent_data.get('abstract', ''))} 자")
        print(f"청구항 길이: {len(patent_data.get('claim', ''))} 자")
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {patent_file}")
        exit(1)

    # 테스트할 모델 목록
    models = [
        "command-r7b-12-2024",
        "command-r-08-2024",
        "command-a-03-2025",
        "command-a-reasoning-08-2025",
    ]

    system_prompt = "당신은 특허 분석 전문가입니다. 기술적 내용을 정확하게 분석해주세요. 한국어로 답변해주세요."

    # ========================================
    # 테스트 1: 청구항 분석
    # ========================================
    print("\n" + "=" * 70)
    print("테스트 1: 청구항 분석")
    print("=" * 70 + "\n")

    claim_prompt = f"""다음 특허 청구항을 분석해주세요:

{patent_data.get('claim', '')}

다음 항목을 포함해주세요:
1. 청구항 유형 (독립항/종속항)
2. 구성요소 분해
3. 권리범위 해석
4. 핵심 한정 요소
"""

    results_claim = []
    for model in models:
        try:
            result = run_model(model, claim_prompt, system_prompt)
            results_claim.append(result)
        except Exception as e:
            print(f"[ERROR] {model}: {e}\n")
            results_claim.append({"model": model, "error": str(e)})

    # 청구항 텍스트 정보 계산
    claim_text = patent_data.get('claim', '')
    claim_char_count = len(claim_text)
    claim_estimated_tokens = claim_char_count // 3  # 한글 기준 대략 3자당 1토큰
    claim_context_usage = (claim_estimated_tokens / 128000) * 100

    claim_info = {
        "char_count": claim_char_count,
        "estimated_tokens": claim_estimated_tokens,
        "context_usage": claim_context_usage,
    }

    # ========================================
    # 테스트 2: 요약 분석
    # ========================================
    print("\n" + "=" * 70)
    print("테스트 2: 요약 분석")
    print("=" * 70 + "\n")

    summary_prompt = f"""다음 특허 요약을 분석하고 핵심 내용을 정리해주세요:

{patent_data.get('abstract', '')}

다음 항목을 포함해주세요:
1. 핵심 기술 (2-3문장)
2. 주요 구성요소
3. 기술적 효과
4. 기술 분야
"""

    results_summary = []
    for model in models:
        try:
            result = run_model(model, summary_prompt, system_prompt)
            results_summary.append(result)
        except Exception as e:
            print(f"[ERROR] {model}: {e}\n")
            results_summary.append({"model": model, "error": str(e)})

    # 요약 텍스트 정보 계산
    abstract_text = patent_data.get('abstract', '')
    abstract_char_count = len(abstract_text)
    abstract_estimated_tokens = abstract_char_count // 3
    abstract_context_usage = (abstract_estimated_tokens / 128000) * 100

    abstract_info = {
        "char_count": abstract_char_count,
        "estimated_tokens": abstract_estimated_tokens,
        "context_usage": abstract_context_usage,
    }

    # ========================================
    # 결과 저장 (하나의 파일로 통합)
    # ========================================
    save_combined_results(
        claim_results=results_claim,
        summary_results=results_summary,
        claim_info=claim_info,
        abstract_info=abstract_info,
        patent_title=patent_data.get('title', 'N/A')
    )

    # ========================================
    # 최종 요약 출력
    # ========================================
    print("\n" + "=" * 70)
    print("최종 비용 요약")
    print("=" * 70)

    all_results = results_claim + results_summary
    total_cost = sum(r.get("cost", {}).get("total_cost", 0) for r in all_results if "cost" in r)
    total_input = sum(r.get("input_tokens", 0) for r in all_results if "input_tokens" in r)
    total_output = sum(r.get("output_tokens", 0) for r in all_results if "output_tokens" in r)

    print(f"총 입력 토큰: {total_input:,}")
    print(f"총 출력 토큰: {total_output:,}")
    print(f"총 테스트 비용: ${total_cost:.6f}")
