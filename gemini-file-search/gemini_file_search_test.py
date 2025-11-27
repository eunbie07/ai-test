# 파일: gemini_file_search_test.py
# Gemini API File Search 기능 테스트
# - uploadToFileSearchStore API를 활용한 파일 업로드
# - 파이썬 변수를 통한 파일 전달
# - 프롬프트에서 문서 참조 방식 테스트

import os
import time
import tempfile
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
    # 파일 업로드 (비동기 작업)
    operation = client.file_search_stores.upload_to_file_search_store(
        file=file_path,
        file_search_store_name=store_name,
        config={"display_name": os.path.basename(file_path)}
    )

    # 업로드 완료 대기
    print(f"파일 업로드 중... (최대 60초 대기)")
    wait_count = 0
    while not operation.done and wait_count < 12:
        time.sleep(5)
        operation = client.operations.get(operation)
        wait_count += 1
        print(f"  대기 중... ({wait_count * 5}초)")

    if operation.done:
        print(f"파일 업로드 완료")
    else:
        print(f"파일 업로드 시간 초과")

    return operation


def upload_bytes_to_store(client, store_name: str, content: bytes, filename: str, mime_type: str = "text/plain", custom_metadata: list = None):
    """
    바이트 데이터(변수)를 File Search 스토어에 업로드
    - 파일이 아닌 메모리 상의 데이터를 직접 전달
    - 임시 파일을 생성하여 업로드 후 삭제
    - custom_metadata: 메타데이터 필터링용 키-값 쌍 리스트
      예: [{"key": "author", "string_value": "홍길동"}, {"key": "year", "numeric_value": 2025}]
    """
    # 임시 파일 생성
    suffix = os.path.splitext(filename)[1] or ".txt"
    with tempfile.NamedTemporaryFile(mode='wb', suffix=suffix, delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_path = tmp_file.name

    # config 구성
    upload_config = {
        "display_name": filename,
        "mime_type": mime_type
    }
    if custom_metadata:
        upload_config["custom_metadata"] = custom_metadata

    try:
        # 파일 업로드 (비동기 작업)
        operation = client.file_search_stores.upload_to_file_search_store(
            file=tmp_path,
            file_search_store_name=store_name,
            config=upload_config
        )

        # 업로드 완료 대기
        print(f"바이트 데이터 업로드 중... (최대 60초 대기)")
        wait_count = 0
        while not operation.done and wait_count < 12:
            time.sleep(5)
            operation = client.operations.get(operation)
            wait_count += 1
            print(f"  대기 중... ({wait_count * 5}초)")

        if operation.done:
            print(f"바이트 데이터 업로드 완료: {filename}")
        else:
            print(f"바이트 데이터 업로드 시간 초과")

        return operation
    finally:
        # 임시 파일 삭제
        os.unlink(tmp_path)


def list_documents(client, store_name: str):
    """
    스토어 내 문서 목록 조회
    - Documents API: documents.list
    """
    print(f"\n스토어 내 문서 목록 조회 중...")
    documents = client.file_search_stores.list_documents(name=store_name)

    doc_list = []
    for doc in documents:
        doc_info = {
            "name": doc.name,
            "display_name": getattr(doc, 'display_name', 'N/A'),
            "state": getattr(doc, 'state', 'N/A'),
            "size_bytes": getattr(doc, 'size_bytes', 'N/A'),
            "mime_type": getattr(doc, 'mime_type', 'N/A'),
        }
        doc_list.append(doc_info)
        print(f"  - {doc_info['display_name']} ({doc_info['state']})")

    return doc_list


def get_document(client, document_name: str):
    """
    특정 문서 정보 조회
    - Documents API: documents.get
    """
    doc = client.file_search_stores.get_document(name=document_name)

    doc_info = {
        "name": doc.name,
        "display_name": getattr(doc, 'display_name', 'N/A'),
        "state": getattr(doc, 'state', 'N/A'),
        "size_bytes": getattr(doc, 'size_bytes', 'N/A'),
        "mime_type": getattr(doc, 'mime_type', 'N/A'),
        "create_time": getattr(doc, 'create_time', 'N/A'),
        "update_time": getattr(doc, 'update_time', 'N/A'),
        "custom_metadata": getattr(doc, 'custom_metadata', []),
    }

    print(f"문서 정보: {doc_info['display_name']}")
    print(f"  - 상태: {doc_info['state']}")
    print(f"  - 크기: {doc_info['size_bytes']} bytes")
    print(f"  - MIME: {doc_info['mime_type']}")

    return doc_info


def delete_document(client, document_name: str, force: bool = False):
    """
    문서 삭제
    - Documents API: documents.delete
    - force=True: 관련 Chunk도 함께 삭제
    """
    print(f"문서 삭제 중: {document_name}")
    client.file_search_stores.delete_document(name=document_name, force=force)
    print(f"문서 삭제 완료")


def get_store_info(client, store_name: str):
    """
    스토어 정보 조회
    - FileSearchStores API: fileSearchStores.get
    """
    store = client.file_search_stores.get(name=store_name)

    store_info = {
        "name": store.name,
        "display_name": getattr(store, 'display_name', 'N/A'),
        "active_documents_count": getattr(store, 'active_documents_count', 0),
        "pending_documents_count": getattr(store, 'pending_documents_count', 0),
        "failed_documents_count": getattr(store, 'failed_documents_count', 0),
        "size_bytes": getattr(store, 'size_bytes', 0),
    }

    print(f"\n스토어 정보: {store_info['display_name']}")
    print(f"  - 활성 문서: {store_info['active_documents_count']}개")
    print(f"  - 처리 중: {store_info['pending_documents_count']}개")
    print(f"  - 실패: {store_info['failed_documents_count']}개")
    print(f"  - 총 크기: {store_info['size_bytes']} bytes")

    return store_info


def delete_store(client, store_name: str, force: bool = True):
    """
    스토어 삭제
    - FileSearchStores API: fileSearchStores.delete
    - force=True: 관련 문서도 함께 삭제
    """
    print(f"스토어 삭제 중: {store_name}")
    client.file_search_stores.delete(name=store_name, force=force)
    print(f"스토어 삭제 완료")


def query_with_file_search(client, store_name: str, query: str, doc_reference_style: str = "문서", metadata_filter: str = None):
    """
    File Search를 활용한 쿼리 실행
    - doc_reference_style: 프롬프트에서 문서를 어떻게 지칭할지 테스트
      예: "문서", "파일", "자료", "업로드된 문서", "첨부된 파일" 등
    - metadata_filter: 메타데이터 필터링 (예: "author=홍길동", "year>2024")
    """
    # 다양한 문서 참조 방식으로 프롬프트 구성
    prompt = f"제공된 {doc_reference_style}를 바탕으로 다음 질문에 답변해주세요: {query}"

    # FileSearch 설정 구성
    file_search_config = types.FileSearch(
        file_search_store_names=[store_name]
    )

    # 메타데이터 필터가 있으면 추가
    if metadata_filter:
        file_search_config = types.FileSearch(
            file_search_store_names=[store_name],
            metadata_filter=metadata_filter
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=file_search_config
                )
            ]
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
        print(f" 테스트: '{style}'로 지칭")
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
            print(f" 오류: {e}")

    return results


def save_results_to_md(store_info: dict, doc_list: list, results: dict, test_query: str):
    """테스트 결과를 MD 파일로 저장"""
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_result_{timestamp}.md"

    lines = []
    lines.append("# Gemini File Search API 테스트 결과")
    lines.append("")
    lines.append(f"**테스트 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # 결과 요약 테이블
    lines.append("## 테스트 결과 요약")
    lines.append("")
    lines.append("| 문서 참조 방식 | 결과 |")
    lines.append("|--------------|------|")
    for style, result in results.items():
        status = "O 성공" if result["success"] else "X 실패"
        lines.append(f"| {style} | {status} |")
    lines.append("")

    # 스토어 정보
    lines.append("## 스토어 정보")
    lines.append("")
    if store_info:
        lines.append(f"- **스토어명**: {store_info.get('display_name', 'N/A')}")
        lines.append(f"- **활성 문서**: {store_info.get('active_documents_count', 0)}개")
        lines.append(f"- **처리 중**: {store_info.get('pending_documents_count', 0)}개")
        lines.append(f"- **실패**: {store_info.get('failed_documents_count', 0)}개")
        lines.append(f"- **총 크기**: {store_info.get('size_bytes', 0)} bytes")
    else:
        lines.append("스토어 정보를 가져올 수 없습니다.")
    lines.append("")

    # 테스트 쿼리
    lines.append("## 테스트 쿼리")
    lines.append("")
    lines.append(f"> {test_query}")
    lines.append("")

    # 각 참조 방식별 상세 결과
    lines.append("## 상세 결과")
    lines.append("")

    for style, result in results.items():
        lines.append(f"### '{style}' 참조 방식")
        lines.append("")
        if result["success"]:
            answer = result.get("answer", "")
            # 응답이 길면 일부만 표시
            if len(answer) > 500:
                answer = answer[:500] + "..."
            lines.append(f"**응답**:")
            lines.append("```")
            lines.append(answer)
            lines.append("```")

            # grounding 정보가 있으면 추가
            if result.get("grounding"):
                lines.append("")
                lines.append("**인용 정보**: 있음")
        else:
            lines.append(f"**오류**: {result.get('error', 'Unknown error')}")
        lines.append("")

    # 결론
    lines.append("## 결론")
    lines.append("")
    success_count = sum(1 for r in results.values() if r["success"])
    total_count = len(results)
    lines.append(f"- 총 {total_count}개 참조 방식 중 **{success_count}개 성공**")
    lines.append("- File Search 도구가 자동으로 스토어에서 관련 내용을 검색하기 때문에, 프롬프트에서 **어떤 단어로 지칭해도 동일하게 동작**합니다.")
    lines.append("")

    # 파일 저장
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n결과가 {filename} 파일로 저장되었습니다.")
    return filename


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
    print("\n테스트 문서 업로드 중...")
    upload_bytes_to_store(
        client,
        store_name,
        test_document_content,
        "project_docs.md"
    )

    # 5. 스토어 정보 확인 (Documents API 활용)
    print("\n" + "=" * 60)
    print("스토어 및 문서 정보 확인")
    print("=" * 60)

    store_info = None
    doc_list = []
    try:
        store_info = get_store_info(client, store_name)
        doc_list = list_documents(client, store_name)
    except Exception as e:
        print(f"정보 조회 실패 (API 미지원 가능): {e}")

    # 6. 다양한 문서 참조 방식 테스트
    test_query = "이 프로젝트의 주요 기술 스택은 무엇인가요?"

    print("\n" + "=" * 60)
    print("문서 참조 방식별 테스트 시작")
    print("=" * 60)

    results = test_document_reference_styles(client, store_name, test_query)

    # 7. 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)

    for style, result in results.items():
        status = "성공" if result["success"] else "실패"
        print(f"  - '{style}': {status}")

    # 8. 결과를 MD 파일로 저장
    save_results_to_md(store_info, doc_list, results, test_query)

    # 9. 스토어 정리 (선택사항 - 주석 해제하면 삭제됨)
    # delete_store(client, store_name, force=True)

    return results


if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print(" 오류: GEMINI_API_KEY 또는 GOOGLE_API_KEY 환경변수를 설정해주세요.")
        print("   예: export GEMINI_API_KEY='your-api-key'")
    else:
        results = main()
