import os
import httpx
from typing import Dict, Any


NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
NAVER_API_HEADERS = {
    "X-Naver-Client-Id": NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
}
NAVER_API_ENDPOINT = "https://openapi.naver.com/v1"


async def search_blog_naver(
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "sim"
) -> str:
    """
    네이버 검색의 블로그 검색 결과를 반환합니다.
    블로그 포스트, 개인 블로그, 기업 블로그 등의 블로그 콘텐츠를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
        display (int): 한 번에 표시할 검색 결과 개수 (기본값: 10, 최대: 100)
        start (int): 검색 시작 위치 (기본값: 1, 최대: 1000)
        sort (str): 정렬 방법 - "sim"(정확도순), "date"(최신순) (기본값: "sim")

    Returns:
        str: 블로그 검색 결과 JSON 문자열
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{NAVER_API_ENDPOINT}/search/blog.json",
            params={
                "query": query,
                "display": display,
                "start": start,
                "sort": sort,
            },
            headers=NAVER_API_HEADERS,
        )
        response.raise_for_status()
        return response.text


async def search_local_naver(
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "random"
) -> str:
    """
    네이버 지역 서비스에 등록된 지역별 업체 및 상호 검색 결과를 반환합니다.
    음식점, 카페, 병원, 약국, 편의점 등 지역 기반 업체 정보를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
        display (int): 한 번에 표시할 검색 결과 개수 (기본값: 10, 최대: 100)
        start (int): 검색 시작 위치 (기본값: 1, 최대: 1000)
        sort (str): 정렬 방법 - "random"(랜덤순), "comment"(리뷰순), "count"(방문자순) (기본값: "random")

    Returns:
        str: 지역 검색 결과 JSON 문자열
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{NAVER_API_ENDPOINT}/search/local.json",
            params={
                "query": query,
                "display": display,
                "start": start,
                "sort": sort,
            },
            headers=NAVER_API_HEADERS,
        )
        response.raise_for_status()
        return response.text


async def search_web_naver(
    query: str,
    display: int = 10,
    start: int = 1
) -> str:
    """
    네이버 검색의 웹 문서 검색 결과를 반환합니다.
    일반 웹페이지, 홈페이지, 기업 사이트 등의 웹 콘텐츠를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
        display (int): 한 번에 표시할 검색 결과 개수 (기본값: 10, 최대: 100)
        start (int): 검색 시작 위치 (기본값: 1, 최대: 1000)

    Returns:
        str: 웹 검색 결과 JSON 문자열
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{NAVER_API_ENDPOINT}/search/webkr.json",
            params={
                "query": query,
                "display": display,
                "start": start,
            },
            headers=NAVER_API_HEADERS,
        )
        response.raise_for_status()
        return response.text