# 파일: ai_tool_demo.py

import os
from datetime import datetime
from typing import List, Dict, Any

import requests
from openai import OpenAI
import google.generativeai as genai
import anthropic


# 1) 우리가 만든 FastAPI 툴 (BigQuery 프록시)를 직접 호출하는 함수
def search_patents_tool(keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    FastAPI의 /patents/search 엔드포인트를 호출해서
    Google Patents 검색 결과를 가져온다.
    """
    url = "http://localhost:8000/patents/search"
    params = {"keyword": keyword, "limit": limit}
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
        model="gpt-4.1-mini",  # 필요하면 gpt-4.1 등으로 변경
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

    model = genai.GenerativeModel("gemini-2.0-flash")
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
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_content}
        ],
    )

    return response.content[0].text


# 5) 이전처럼 콘솔에 간단히 찍어보는 함수 (옵션)
def pretty_print_patents(patents: List[Dict[str, Any]]) -> None:
    print("=== 특허 검색 결과 요약 (raw) ===")
    for i, p in enumerate(patents, start=1):
        title = p["title_localized"][0]["text"] if p["title_localized"] else ""
        pub_date = p.get("publication_date")
        print(f"{i}. [{p['publication_number']}] ({pub_date})")
        print(f"   {title}")
        print()


if __name__ == "__main__":
    # 1) 로컬 FastAPI 툴 호출해서 graphite 관련 특허 5건 가져오기
    keyword = "graphite"
    patents = search_patents_tool(keyword=keyword, limit=5)

    # 2) raw 데이터도 한번 보고 싶으면 (옵션)
    pretty_print_patents(patents)

    question = "이 graphite 관련 특허들의 공통적인 기술 방향과 특징을 간단히 정리해줘."

    # 결과 저장용 리스트
    results = []
    results.append(f"테스트 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results.append(f"검색 키워드: {keyword}")
    results.append(f"조회 건수: {len(patents)}건")
    results.append("")
    results.append("=" * 50)
    results.append("특허 검색 결과 (Raw)")
    results.append("=" * 50)
    for i, p in enumerate(patents, start=1):
        title = p["title_localized"][0]["text"] if p["title_localized"] else ""
        pub_date = p.get("publication_date")
        results.append(f"{i}. [{p['publication_number']}] ({pub_date})")
        results.append(f"   {title}")
    results.append("")

    # 3) GPT 요약
    print("\n=== GPT 요약 결과 ===")
    try:
        gpt_answer = ask_gpt_about_patents(question, patents)
        print(gpt_answer)
        results.append("=" * 50)
        results.append("GPT 요약 결과")
        results.append("=" * 50)
        results.append(gpt_answer)
        results.append("")
    except Exception as e:
        print(f"GPT 호출 실패: {e}")
        results.append(f"GPT 호출 실패: {e}")
        results.append("")

    # 4) Gemini 요약
    print("\n=== Gemini 요약 결과 ===")
    try:
        gemini_answer = ask_gemini_about_patents(question, patents)
        print(gemini_answer)
        results.append("=" * 50)
        results.append("Gemini 요약 결과")
        results.append("=" * 50)
        results.append(gemini_answer)
        results.append("")
    except Exception as e:
        print(f"Gemini 호출 실패: {e}")
        results.append(f"Gemini 호출 실패: {e}")
        results.append("")

    # 5) Claude 요약
    print("\n=== Claude 요약 결과 ===")
    try:
        claude_answer = ask_claude_about_patents(question, patents)
        print(claude_answer)
        results.append("=" * 50)
        results.append("Claude 요약 결과")
        results.append("=" * 50)
        results.append(claude_answer)
        results.append("")
    except Exception as e:
        print(f"Claude 호출 실패: {e}")
        results.append(f"Claude 호출 실패: {e}")
        results.append("")

    # 6) 결과를 txt 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_result_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    print(f"\n결과가 {filename} 파일로 저장되었습니다.")
