# 파일: ai_tool_demo.py

import os
from datetime import datetime
from typing import List, Dict, Any

import requests
from openai import OpenAI
import google.generativeai as genai
import anthropic


# 1) 우리가 만든 FastAPI 툴 (BigQuery 프록시)를 직접 호출하는 함수
def search_patents_tool(
    keyword: str,
    limit: int = 5,
    countries: str | None = None
) -> List[Dict[str, Any]]:
    """
    FastAPI의 /patents/search 엔드포인트를 호출해서
    Google Patents 검색 결과를 가져온다.

    Args:
        keyword: 검색 키워드
        limit: 검색 결과 수 제한
        countries: 국가 코드 (쉼표 구분, 예: "US,KR")
    """
    url = "http://localhost:8000/patents/search"
    params = {"keyword": keyword, "limit": limit}
    if countries:
        params["countries"] = countries
    resp = requests.get(url, params=params, timeout=30)

    resp.raise_for_status()
    return resp.json()


# 2) GPT에게 "툴 결과를 넘겨서" 자연어 요약/정리 요청
def ask_gpt_about_patents(question: str, patents: List[Dict[str, Any]]) -> str:
    """
    - 사용자의 자연어 질문(question)
    - /patents/search 툴 결과(patents) 를 함께 GPT에 넘겨서
      사람이 읽기 좋은 답변을 받는 함수
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # GPT가 읽기 쉬운 형태로 특허 리스트를 약간 정리해서 넘겨주자
    # (그대로 JSON 넘겨도 되지만, 여기선 핵심 필드만 추려서 텍스트로 구성)
    patents_text_lines = []
    for p in patents:
        title = p["title_localized"][0]["text"] if p["title_localized"] else ""
        pub_date = p.get("publication_date")
        pub_no = p.get("publication_number")
        patents_text_lines.append(f"- {pub_no} ({pub_date}): {title}")

    patents_block = "\n".join(patents_text_lines)

    system_prompt = (
        "너는 특허 분석을 도와주는 AI 어시스턴트야. "
        "아래에 제공된 특허 검색 결과를 기반으로만 답변해야 해. "
        "모르는 내용은 추측하지 말고, 결과 안에서 확인 가능한 내용만 정리해줘."
    )

    user_content = (
        f"사용자 질문:\n{question}\n\n"
        f"다음은 Google Patents에서 'graphite' 키워드로 검색한 결과 일부야:\n"
        f"{patents_block}\n\n"
        "위 내용을 바탕으로, 핵심 내용을 한국어로 정리해줘."
    )

    response = client.responses.create(
        model="gpt-5.1",  # User requested gpt-5.1
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )

    # responses.create() 결과에서 텍스트만 추출
    # (새 SDK 기준)
    output_text = response.output[0].content[0].text
    return output_text


# 3) Gemini에게 특허 요약 요청
def ask_gemini_about_patents(question: str, patents: List[Dict[str, Any]]) -> str:
    """
    Gemini API를 사용해서 특허 검색 결과를 요약/분석
    """
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

    patents_text_lines = []
    for p in patents:
        title = p["title_localized"][0]["text"] if p["title_localized"] else ""
        pub_date = p.get("publication_date")
        pub_no = p.get("publication_number")
        patents_text_lines.append(f"- {pub_no} ({pub_date}): {title}")

    patents_block = "\n".join(patents_text_lines)

    prompt = (
        "너는 특허 분석을 도와주는 AI 어시스턴트야. "
        "아래에 제공된 특허 검색 결과를 기반으로만 답변해야 해. "
        "모르는 내용은 추측하지 말고, 결과 안에서 확인 가능한 내용만 정리해줘.\n\n"
        f"사용자 질문:\n{question}\n\n"
        f"다음은 Google Patents에서 검색한 결과 일부야:\n"
        f"{patents_block}\n\n"
        "위 내용을 바탕으로, 핵심 내용을 한국어로 정리해줘."
    )

    model = genai.GenerativeModel("gemini-2.5-pro")
    response = model.generate_content(prompt)

    return response.text


# 4) Claude에게 특허 요약 요청
def ask_claude_about_patents(question: str, patents: List[Dict[str, Any]]) -> str:
    """
    Claude API를 사용해서 특허 검색 결과를 요약/분석
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    patents_text_lines = []
    for p in patents:
        title = p["title_localized"][0]["text"] if p["title_localized"] else ""
        pub_date = p.get("publication_date")
        pub_no = p.get("publication_number")
        patents_text_lines.append(f"- {pub_no} ({pub_date}): {title}")

    patents_block = "\n".join(patents_text_lines)

    system_prompt = (
        "너는 특허 분석을 도와주는 AI 어시스턴트야. "
        "아래에 제공된 특허 검색 결과를 기반으로만 답변해야 해. "
        "모르는 내용은 추측하지 말고, 결과 안에서 확인 가능한 내용만 정리해줘."
    )

    user_content = (
        f"사용자 질문:\n{question}\n\n"
        f"다음은 Google Patents에서 검색한 결과 일부야:\n"
        f"{patents_block}\n\n"
        "위 내용을 바탕으로, 핵심 내용을 한국어로 정리해줘."
    )

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_content}
        ],
    )

    return response.content[0].text


# 5) 특허 정보를 마크다운으로 포맷팅하는 함수
def format_patent_markdown(p: Dict[str, Any]) -> str:
    """특허 정보를 마크다운 형식으로 포맷팅"""
    lines = []
    title = p["title_localized"][0]["text"] if p.get("title_localized") else ""
    abstract = p["abstract_localized"][0]["text"] if p.get("abstract_localized") else ""
    assignees = ", ".join([a["name"] for a in p.get("assignee", []) if a.get("name")])
    inventors = ", ".join([inv["name"] for inv in p.get("inventor", []) if inv.get("name")])
    cpc_codes = ", ".join(p.get("cpc", [])[:5])  # 최대 5개만

    lines.append(f"| publication_number | {p.get('publication_number')} |")
    lines.append(f"| application_number | {p.get('application_number')} |")
    lines.append(f"| country_code | {p.get('country_code')} |")
    lines.append(f"| title | {title} |")
    lines.append(f"| publication_date | {p.get('publication_date')} |")
    lines.append(f"| filing_date | {p.get('filing_date')} |")
    lines.append(f"| assignee | {assignees or 'N/A'} |")
    lines.append(f"| inventor | {inventors or 'N/A'} |")
    lines.append(f"| cpc | {cpc_codes or 'N/A'} |")
    if abstract:
        lines.append(f"| abstract | {abstract[:200]}... |")

    return "\n".join(lines)


# 6) 이전처럼 콘솔에 간단히 찍어보는 함수 (옵션)
def pretty_print_patents(patents: List[Dict[str, Any]]) -> None:
    print("=== 특허 검색 결과 요약 (raw) ===")
    for i, p in enumerate(patents, start=1):
        title = p["title_localized"][0]["text"] if p.get("title_localized") else ""
        pub_date = p.get("publication_date")
        assignees = ", ".join([a["name"] for a in p.get("assignee", []) if a.get("name")])
        print(f"{i}. [{p['publication_number']}] ({pub_date})")
        print(f"   제목: {title}")
        print(f"   출원인: {assignees or 'N/A'}")
        print()


if __name__ == "__main__":
    # 1) 로컬 FastAPI 툴 호출해서 graphite 관련 특허 (미국+한국) 가져오기
    # 영어 + 한국어 키워드를 쉼표로 구분해서 전달
    keyword = "graphite,흑연,그래파이트"
    countries = "US,KR"

    # US 6건, KR 6건 각각 가져오기
    us_patents = search_patents_tool(keyword=keyword, limit=6, countries="US")
    kr_patents = search_patents_tool(keyword=keyword, limit=6, countries="KR")
    patents = us_patents + kr_patents

    question = "이 graphite 관련 특허들의 공통적인 기술 방향과 특징을 간단히 정리해줘."

    # 결과 저장용 리스트 (마크다운 형식)
    results = []
    results.append("# 특허 검색 테스트 결과")
    results.append("")
    results.append(f"- **테스트 일시:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results.append(f"- **검색 키워드:** {keyword}")
    results.append(f"- **검색 국가:** {countries}")
    results.append(f"- **조회 건수:** {len(patents)}건 (US {len(us_patents)}건 + KR {len(kr_patents)}건)")
    results.append("")
    results.append("---")
    results.append("")
    results.append("## API 사용법")
    results.append("")
    results.append("### 엔드포인트")
    results.append("```")
    results.append("GET /patents/search")
    results.append("```")
    results.append("")
    results.append("### 파라미터")
    results.append("")
    results.append("| 파라미터 | 필수 | 설명 | 예시 |")
    results.append("|----------|------|------|------|")
    results.append("| `keyword` | O | 검색 키워드 (쉼표로 여러 개 가능) | `graphite,흑연,그래파이트` |")
    results.append("| `limit` | X | 결과 수 제한 (기본값: 20, 최대: 100) | `10` |")
    results.append("| `countries` | X | 국가 코드 (쉼표 구분) | `US,KR,JP,CN,EP` |")
    results.append("")
    results.append("### 쿼리 예시")
    results.append("")
    results.append("**1. 단일 키워드 (영어)**")
    results.append("```")
    results.append("/patents/search?keyword=graphite&limit=10&countries=US")
    results.append("```")
    results.append("")
    results.append("**2. 다중 키워드 (영어 + 한국어) - 한국 특허 검색 시 필수**")
    results.append("```")
    results.append("/patents/search?keyword=graphite,흑연,그래파이트&limit=10&countries=KR")
    results.append("```")
    results.append("")
    results.append("**3. 여러 국가 동시 검색**")
    results.append("```")
    results.append("/patents/search?keyword=battery,배터리,电池&limit=20&countries=US,KR,CN,JP")
    results.append("```")
    results.append("")
    results.append("### 주의사항")
    results.append("")
    results.append("- **한국(KR) 특허 검색 시**: 반드시 한국어 키워드를 포함해야 합니다")
    results.append("- **중국(CN) 특허 검색 시**: 중국어 간체 키워드를 포함해야 합니다")
    results.append("- **일본(JP) 특허 검색 시**: 일본어 키워드를 포함해야 합니다")
    results.append("- 키워드는 특허 제목(title)에서 검색됩니다")
    results.append("")
    results.append("---")
    results.append("")
    results.append("## 특허 검색 결과 (Raw)")
    results.append("")
    for i, p in enumerate(patents, start=1):
        results.append(f"### [{i}] {p.get('publication_number')}")
        results.append("")
        results.append("| Field | Value |")
        results.append("|-------|-------|")
        results.append(format_patent_markdown(p))
        results.append("")
    results.append("---")
    results.append("")

    # 3) GPT 요약
    print("\n=== GPT 요약 결과 ===")
    try:
        gpt_answer = ask_gpt_about_patents(question, patents)
        print(gpt_answer)
        results.append("## GPT 요약 결과")
        results.append("")
        results.append(gpt_answer)
        results.append("")
        results.append("---")
        results.append("")
    except Exception as e:
        print(f"GPT 호출 실패: {e}")
        results.append(f"## GPT 요약 결과")
        results.append("")
        results.append(f"> 호출 실패: {e}")
        results.append("")

    # 4) Gemini 요약
    print("\n=== Gemini 요약 결과 ===")
    try:
        gemini_answer = ask_gemini_about_patents(question, patents)
        print(gemini_answer)
        results.append("## Gemini 요약 결과")
        results.append("")
        results.append(gemini_answer)
        results.append("")
        results.append("---")
        results.append("")
    except Exception as e:
        print(f"Gemini 호출 실패: {e}")
        results.append(f"## Gemini 요약 결과")
        results.append("")
        results.append(f"> 호출 실패: {e}")
        results.append("")

    # 5) Claude 요약
    print("\n=== Claude 요약 결과 ===")
    try:
        claude_answer = ask_claude_about_patents(question, patents)
        print(claude_answer)
        results.append("## Claude 요약 결과")
        results.append("")
        results.append(claude_answer)
        results.append("")
    except Exception as e:
        print(f"Claude 호출 실패: {e}")
        results.append(f"## Claude 요약 결과")
        results.append("")
        results.append(f"> 호출 실패: {e}")
        results.append("")

    # 6) 결과를 md 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_result_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    print(f"\n결과가 {filename} 파일로 저장되었습니다.")
