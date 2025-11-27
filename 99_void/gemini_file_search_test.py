# 파일: gemini_file_search_test.py
# Gemini API File Search 기능 테스트
# - uploadToFileSearchStore API를 활용한 파일 업로드
# - 파이썬 변수를 통한 파일 전달
# - 프롬프트에서 문서 참조 방식 테스트

import os
from google import genai
from google.genai import types

# API 키 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def create_client():
    """Gemini API 클라이언트 생성"""
    return genai.Client(api_key=GEMINI_API_KEY)


def create_file_search_store(client, store_name: str = "test-store"):
    """파일 검색 스토어 생성"""
    file_search_store = client.file_search_stores.create(
        config=types.CreateFileSearchStoreConfig(display_name=store_name)
    )
    print(f"스토어 생성 완료: {file_search_store.name}")
    return file_search_store


def upload_file_to_store(client, store_name: str, file_path: str):
    """
    파일을 File Search 스토어에 직접 업로드
    - UI가 아닌 파이썬 코드로 파일 전달
    """
    # 파일 업로드
    uploaded_file = client.file_search_stores.upload_file(
        name=store_name,
        file=file_path,  # 로컬 파일 경로
    )
    print(f"파일 업로드 완료: {uploaded_file.name}")
    return uploaded_file


def upload_bytes_to_store(client, store_name: str, content: bytes, filename: str):
    """
    바이트 데이터(변수)를 File Search 스토어에 업로드
    - 파일이 아닌 메모리 상의 데이터를 직접 전달
    """
    import io

    # 바이트를 파일류 객체로 변환
    file_obj = io.BytesIO(content)
    file_obj.name = filename  # 파일명 지정

    uploaded_file = client.file_search_stores.upload_file(
        name=store_name,
        file=file_obj,
    )
    print(f"바이트 데이터 업로드 완료: {uploaded_file.name}")
    return uploaded_file


def query_with_file_search(client, store_name: str, query: str, doc_reference_style: str = "문서"):
    """
    File Search를 활용한 쿼리 실행
    - doc_reference_style: 프롬프트에서 문서를 어떻게 지칭할지 테스트
      예: "문서", "파일", "자료", "업로드된 문서", "첨부된 파일" 등
    """
    # File Search 도구 설정
    file_search_tool = types.Tool(
        file_search=types.FileSearch(
            file_search_store_ids=[store_name]
        )
    )

    # 다양한 문서 참조 방식으로 프롬프트 구성
    prompt = f"제공된 {doc_reference_style}를 바탕으로 다음 질문에 답변해주세요: {query}"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[file_search_tool],
        )
    )

    return response


def test_document_reference_styles(client, store_name: str, query: str):
    """
    다양한 문서 참조 방식 테스트
    - 어떤 표현이 가장 자연스럽고 효과적인지 비교
    """
    reference_styles = [
        "문서",
        "파일",
        "자료",
        "업로드된 문서",
        "첨부된 파일",
        "제공된 자료",
        "참고 문서",
    ]

    results = {}

    for style in reference_styles:
        print(f"\n{'='*50}")
        print(f"📝 테스트: '{style}'로 지칭")
        print(f"{'='*50}")

        try:
            response = query_with_file_search(client, store_name, query, style)

            # 응답 텍스트 추출
            answer = response.text if hasattr(response, 'text') else str(response.candidates[0].content.parts[0].text)

            # grounding_metadata (인용 정보) 확인
            grounding_info = None
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    grounding_info = candidate.grounding_metadata

            results[style] = {
                "answer": answer,
                "grounding": grounding_info,
                "success": True
            }

            print(f"응답: {answer[:200]}..." if len(answer) > 200 else f"응답: {answer}")
            if grounding_info:
                print(f"인용 정보: {grounding_info}")

        except Exception as e:
            results[style] = {
                "error": str(e),
                "success": False
            }
            print(f"X 오류: {e}")

    return results


def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("Gemini File Search API 테스트")
    print("=" * 60)

    # 1. 클라이언트 생성
    client = create_client()
    print("클라이언트 생성 완료")

    # 2. File Search 스토어 생성
    store = create_file_search_store(client, "test-doc-store")
    store_name = store.name

    # 3. 테스트용 문서 내용 (파이썬 변수로 정의)
    test_document_content = """
    # 프로젝트 기술 문서

    ## 1. 개요
    이 프로젝트는 AI 기반 특허 분석 시스템입니다.
    주요 기능으로는 특허 검색, 분석, 요약이 있습니다.

    ## 2. 기술 스택
    - Python 3.11
    - FastAPI
    - Google BigQuery
    - OpenAI GPT-4
    - Gemini API

    ## 3. 주요 기능
    - 키워드 기반 특허 검색
    - AI를 활용한 특허 요약
    - 기술 동향 분석

    ## 4. 사용 방법
    1. API 키 설정
    2. 검색 키워드 입력
    3. 결과 확인 및 분석
    """.encode('utf-8')

    # 4. 바이트 데이터로 파일 업로드 (파이썬 변수 활용)
    print("\n📤 테스트 문서 업로드 중...")
    upload_bytes_to_store(
        client,
        store_name,
        test_document_content,
        "project_docs.md"
    )

    # 5. 다양한 문서 참조 방식 테스트
    test_query = "이 프로젝트의 주요 기술 스택은 무엇인가요?"

    print("\n" + "=" * 60)
    print(" 문서 참조 방식별 테스트 시작")
    print("=" * 60)

    results = test_document_reference_styles(client, store_name, test_query)

    # 6. 결과 요약
    print("\n" + "=" * 60)
    print(" 테스트 결과 요약")
    print("=" * 60)

    for style, result in results.items():
        status = " 성공" if result["success"] else " 실패"
        print(f"  - '{style}': {status}")

    # 7. 스토어 정리 (선택사항)
    # client.file_search_stores.delete(name=store_name)
    # print(f"\n🗑️ 스토어 삭제 완료: {store_name}")

    return results


if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print(" 오류: GEMINI_API_KEY 또는 GOOGLE_API_KEY 환경변수를 설정해주세요.")
        print("   예: export GEMINI_API_KEY='your-api-key'")
    else:
        results = main()
