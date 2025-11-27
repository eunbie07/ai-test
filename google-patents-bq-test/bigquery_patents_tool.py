# 파일명: bigquery_patents_tool.py

from typing import List, Dict, Any
from google.cloud import bigquery

# gcloud init 에서 쓰는 프로젝트 ID
PROJECT_ID = "project-69deab36-6e87-4730-9f1"


def _normalize_localized_text(value) -> List[Dict[str, Any]]:
    """
    title_localized, abstract_localized 등 localized 컬럼을 파이썬 dict 리스트로 정리.
    """
    items: List[Dict[str, Any]] = []

    if not value:
        return items

    for t in value:
        if isinstance(t, dict):
            text = t.get("text")
            language = t.get("language")
        else:
            text = getattr(t, "text", None)
            language = getattr(t, "language", None)

        items.append({
            "text": text,
            "language": language,
        })

    return items


def _normalize_assignee(value) -> List[Dict[str, Any]]:
    """
    assignee(출원인/권리자) 컬럼을 파이썬 dict 리스트로 정리.
    BigQuery에서 assignee는 문자열 배열로 오고,
    assignee_harmonized는 객체 배열로 옴.
    """
    items: List[Dict[str, Any]] = []

    if not value:
        return items

    for a in value:
        # 문자열인 경우 (assignee 컬럼)
        if isinstance(a, str):
            items.append({
                "name": a,
                "country_code": None,
            })
        # dict인 경우 (assignee_harmonized 컬럼)
        elif isinstance(a, dict):
            name = a.get("name")
            country = a.get("country_code")
            items.append({
                "name": name,
                "country_code": country,
            })
        # 객체인 경우
        else:
            name = getattr(a, "name", None)
            country = getattr(a, "country_code", None)
            # name이 없으면 문자열로 변환 시도
            if name is None:
                name = str(a) if a else None
            items.append({
                "name": name,
                "country_code": country,
            })

    return items


def _normalize_inventor(value) -> List[Dict[str, Any]]:
    """
    inventor(발명자) 컬럼을 파이썬 dict 리스트로 정리.
    BigQuery에서 inventor는 문자열 배열로 오고,
    inventor_harmonized는 객체 배열로 옴.
    """
    items: List[Dict[str, Any]] = []

    if not value:
        return items

    for inv in value:
        # 문자열인 경우 (inventor 컬럼)
        if isinstance(inv, str):
            items.append({
                "name": inv,
                "country_code": None,
            })
        # dict인 경우 (inventor_harmonized 컬럼)
        elif isinstance(inv, dict):
            name = inv.get("name")
            country = inv.get("country_code")
            items.append({
                "name": name,
                "country_code": country,
            })
        # 객체인 경우
        else:
            name = getattr(inv, "name", None)
            country = getattr(inv, "country_code", None)
            # name이 없으면 문자열로 변환 시도
            if name is None:
                name = str(inv) if inv else None
            items.append({
                "name": name,
                "country_code": country,
            })

    return items


def _normalize_cpc(value) -> List[str]:
    """
    cpc(CPC 분류코드) 컬럼을 코드 리스트로 정리.
    """
    items: List[str] = []

    if not value:
        return items

    for c in value:
        if isinstance(c, dict):
            code = c.get("code")
        else:
            code = getattr(c, "code", None)

        if code:
            items.append(code)

    return items


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


def search_patents_by_keyword(
    keywords: str | List[str],
    limit: int = 20,
    country_codes: List[str] | None = None
) -> List[Dict[str, Any]]:
    """
    제목에 keyword가 들어가는 특허 검색

    Args:
        keywords: 검색 키워드 (문자열 또는 리스트).
                  예: "graphite" 또는 ["graphite", "흑연", "그래파이트"]
        limit: 검색 결과 수 제한
        country_codes: 국가 코드 리스트 (예: ["US", "KR"]). None이면 전체 국가.
    """
    client = bigquery.Client(project=PROJECT_ID)

    # 키워드를 리스트로 변환
    if isinstance(keywords, str):
        keyword_list = [keywords]
    else:
        keyword_list = keywords

    # 국가 필터 조건 생성
    if country_codes:
        country_filter = "AND country_code IN UNNEST(@country_codes)"
    else:
        country_filter = ""

    # 여러 키워드에 대한 OR 조건 생성
    keyword_conditions = " OR ".join([
        f"LOWER(tl.text) LIKE @pattern_{i}" for i in range(len(keyword_list))
    ])

    # UNNEST를 사용해서 title_localized 배열 안의 text를 검색
    query = f"""
    SELECT
      publication_number,
      application_number,
      country_code,
      title_localized,
      abstract_localized,
      publication_date,
      filing_date,
      assignee,
      inventor,
      cpc
    FROM
      `bigquery-public-data.patents.publications`
    WHERE
      EXISTS (
        SELECT 1
        FROM UNNEST(title_localized) AS tl
        WHERE {keyword_conditions}
      )
      {country_filter}
    LIMIT @limit;
    """

    query_params = [
        bigquery.ScalarQueryParameter(
            "limit", "INT64", limit
        ),
    ]

    # 각 키워드에 대한 파라미터 추가
    for i, kw in enumerate(keyword_list):
        query_params.append(
            bigquery.ScalarQueryParameter(
                f"pattern_{i}", "STRING", f"%{kw.lower()}%"
            )
        )

    if country_codes:
        query_params.append(
            bigquery.ArrayQueryParameter(
                "country_codes", "STRING", country_codes
            )
        )

    job_config = bigquery.QueryJobConfig(
        query_parameters=query_params
    )

    job = client.query(query, job_config=job_config)
    results: List[Dict[str, Any]] = []

    for row in job:
        titles = _normalize_title_localized(row.title_localized)
        abstract = _normalize_localized_text(row.abstract_localized)
        pub_date = _normalize_date(row.publication_date)
        filing = _normalize_date(row.filing_date)
        assignees = _normalize_assignee(row.assignee)
        inventors = _normalize_inventor(row.inventor)
        cpc_codes = _normalize_cpc(row.cpc)

        results.append({
            "publication_number": row.publication_number,
            "application_number": row.application_number,
            "country_code": row.country_code,
            "title_localized": titles,
            "abstract_localized": abstract,
            "publication_date": pub_date,
            "filing_date": filing,
            "assignee": assignees,
            "inventor": inventors,
            "cpc": cpc_codes,
        })

    return results


if __name__ == "__main__":
    # 영어 + 한국어 키워드로 검색
    keywords = ["graphite", "흑연", "그래파이트"]

    print("===== 키워드 검색: graphite/흑연 (미국 6건) =====")
    us_items = search_patents_by_keyword(keywords, limit=6, country_codes=["US"])
    for item in us_items:
        first_title = item["title_localized"][0]["text"] if item["title_localized"] else ""
        print(f"[{item['country_code']}] {item['publication_number']}: {first_title}")

    print("\n===== 키워드 검색: graphite/흑연 (한국 6건) =====")
    kr_items = search_patents_by_keyword(keywords, limit=6, country_codes=["KR"])
    for item in kr_items:
        first_title = item["title_localized"][0]["text"] if item["title_localized"] else ""
        print(f"[{item['country_code']}] {item['publication_number']}: {first_title}")
