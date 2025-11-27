# 파일: app/main.py

from typing import List, Dict, Any

from fastapi import FastAPI, Query, HTTPException

# 같은 폴더가 아니라 루트에 있으니까 이렇게 import
from bigquery_patents_tool import sample_patents, search_patents_by_keyword


app = FastAPI(
    title="Patent BigQuery Proxy API",
    description="Google Patents Public Data를 BigQuery를 통해 조회하는 프록시 API",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> Dict[str, str]:
    """
    단순 헬스 체크 (서버 떠 있는지만 확인)
    """
    return {"status": "ok"}


@app.get("/patents/sample")
def get_sample_patents(
    limit: int = Query(10, ge=1, le=100)
) -> List[Dict[str, Any]]:
    """
    샘플 특허 리스트 조회.
    내부적으로 bigquery_patents_tool.sample_patents() 호출.
    """
    try:
        return sample_patents(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/patents/search")
def search_patents(
    keyword: str = Query(..., min_length=1, description="검색 키워드 (쉼표 구분으로 여러 개 가능, 예: graphite,흑연)"),
    limit: int = Query(20, ge=1, le=100),
    countries: str = Query(None, description="국가 코드 (쉼표 구분, 예: US,KR)"),
) -> List[Dict[str, Any]]:
    """
    키워드로 특허 제목 검색.
    예: /patents/search?keyword=graphite,흑연&limit=5&countries=US,KR
    """
    try:
        # 쉼표로 구분된 키워드를 리스트로 변환
        keywords = [k.strip() for k in keyword.split(",") if k.strip()]

        country_codes = None
        if countries:
            country_codes = [c.strip().upper() for c in countries.split(",")]
        return search_patents_by_keyword(
            keywords=keywords,
            limit=limit,
            country_codes=country_codes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
