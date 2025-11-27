# 파일명: bigquery_patents_tool.py

from typing import List, Dict, Any
from google.cloud import bigquery

# gcloud init 에서 쓰는 프로젝트 ID
PROJECT_ID = "project-69deab36-6e87-4730-9f1"


def _normalize_title_localized(value) -> List[Dict[str, Any]]:
    """
    title_localized 컬럼을 파이썬 dict 리스트로 정리.
    BigQuery 클라이언트 버전에 따라 dict 또는 객체로 올 수 있으니
    둘 다 처리하게 만든다.
    """
    titles: List[Dict[str, Any]] = []

    if not value:
        return titles

    for t in value:
        # t 가 dict 인 경우
        if isinstance(t, dict):
            text = t.get("text")
            language = t.get("language")
            truncated = t.get("truncated")
        else:
            # t 가 객체(record) 인 경우
            text = getattr(t, "text", None)
            language = getattr(t, "language", None)
            truncated = getattr(t, "truncated", None)

        titles.append({
            "text": text,
            "language": language,
            "truncated": str(truncated).lower() if truncated is not None else "false",
        })

    return titles


def _normalize_date(value) -> str | None:
    """
    publication_date / filing_date 가
    - datetime.date
    - int (예: 19711214)
    - str  (예: "19711214")
    어떤 형태로 와도 문자열 'YYYYMMDD'로 변환.
    """
    if value is None:
        return None

    # datetime.date 또는 datetime.datetime 인 경우
    if hasattr(value, "strftime"):
        return value.strftime("%Y%m%d")

    # int 또는 str 등인 경우는 그냥 str 로 변환
    return str(value)


def sample_patents(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Google Patents Public Data 샘플 몇 개 가져오기
    """
    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
    SELECT
      publication_number,
      title_localized,
      publication_date,
      filing_date
    FROM
      `bigquery-public-data.patents.publications`
    LIMIT {limit};
    """

    job = client.query(query)
    results: List[Dict[str, Any]] = []

    for row in job:
        titles = _normalize_title_localized(row.title_localized)
        pub_date = _normalize_date(row.publication_date)
        filing = _normalize_date(row.filing_date)

        results.append({
            "publication_number": row.publication_number,
            "title_localized": titles,
            "publication_date": pub_date,
            "filing_date": filing,
        })

    # 확인용 출력
    for item in results:
        print(item)

    return results


def search_patents_by_keyword(keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    제목에 keyword가 들어가는 특허 검색
    """
    client = bigquery.Client(project=PROJECT_ID)

    # UNNEST를 사용해서 title_localized 배열 안의 text를 검색
    query = """
    SELECT
      publication_number,
      title_localized,
      publication_date,
      filing_date
    FROM
      `bigquery-public-data.patents.publications`
    WHERE
      EXISTS (
        SELECT 1
        FROM UNNEST(title_localized) AS tl
        WHERE LOWER(tl.text) LIKE @pattern
      )
    LIMIT @limit;
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "pattern", "STRING", f"%{keyword.lower()}%"
            ),
            bigquery.ScalarQueryParameter(
                "limit", "INT64", limit
            ),
        ]
    )

    job = client.query(query, job_config=job_config)
    results: List[Dict[str, Any]] = []

    for row in job:
        titles = _normalize_title_localized(row.title_localized)
        pub_date = _normalize_date(row.publication_date)
        filing = _normalize_date(row.filing_date)

        results.append({
            "publication_number": row.publication_number,
            "title_localized": titles,
            "publication_date": pub_date,
            "filing_date": filing,
        })

    return results


if __name__ == "__main__":
    print("===== 샘플 10건 조회 =====")
    sample_items = sample_patents()

    print("===== 키워드 검색: graphite =====")
    items = search_patents_by_keyword("graphite", limit=5)
    for item in items:
        first_title = item["title_localized"][0]["text"] if item["title_localized"] else ""
        print(item["publication_number"], ":", first_title)
