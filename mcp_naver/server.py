# demo.py
import json
import os

import httpx
import xmltodict
from fastmcp import FastMCP

mcp = FastMCP("Naver OpenAPI", dependencies=["httpx", "xmltodict"])


NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
api_headers = {
    "X-Naver-Client-Id": NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
}

API_ENDPOINT = "https://openapi.naver.com/v1"


@mcp.tool(
    name="search_blog",
    description="Search blog posts on Naver",
)
async def search_blog(
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "sim",
):
    """
    네이버 검색의 블로그 검색 결과를 반환합니다.
    블로그 포스트, 개인 블로그, 기업 블로그 등의 블로그 콘텐츠를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
        display (int, optional): 한 번에 표시할 검색 결과 개수 (기본값: 10, 최대: 100)
        start (int, optional): 검색 시작 위치 (기본값: 1, 최대: 1000)
        sort (str, optional): 정렬 방법 - "sim"(정확도순), "date"(최신순) (기본값: "sim")
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_ENDPOINT}/search/blog.json",
            params={
                "query": query,
                "display": display,
                "start": start,
                "sort": sort,
            },
            headers=api_headers,
        )

        response.raise_for_status()  # Raise an error for bad responses

        return response.text


@mcp.tool(
    name="search_cafe_article",
    description="Search cafe articles on Naver",
)
def search_cafe_article(
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "sim",
):
    """
    네이버 검색의 카페글 검색 결과를 반환합니다.
    네이버 카페 내의 게시글, 토론, 커뮤니티 콘텐츠를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
        display (int, optional): 한 번에 표시할 검색 결과 개수 (기본값: 10, 최대: 100)
        start (int, optional): 검색 시작 위치 (기본값: 1, 최대: 1000)
        sort (str, optional): 정렬 방법 - "sim"(정확도순), "date"(최신순) (기본값: "sim")
    """

    with httpx.Client() as client:
        response = client.get(
            f"{API_ENDPOINT}/search/cafearticle.json",
            params={
                "query": query,
                "display": display,
                "start": start,
                "sort": sort,
            },
            headers=api_headers,
        )

        response.raise_for_status()  # Raise an error for bad responses

        return response.text


@mcp.tool(
    name="search_local",
    description="Search local information on Naver",
)
def search_local(
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "random",
):
    """
    네이버 지역 서비스에 등록된 지역별 업체 및 상호 검색 결과를 반환합니다.
    음식점, 카페, 병원, 약국, 편의점 등 지역 기반 업체 정보를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
        display (int, optional): 한 번에 표시할 검색 결과 개수 (기본값: 10, 최대: 100)
        start (int, optional): 검색 시작 위치 (기본값: 1, 최대: 1000)
        sort (str, optional): 정렬 방법 - "random"(랜덤순), "comment"(리뷰순), "count"(방문자순) (기본값: "random")
    """

    with httpx.Client() as client:
        response = client.get(
            f"{API_ENDPOINT}/search/local.json",
            params={
                "query": query,
                "display": display,
                "start": start,
                "sort": sort,
            },
            headers=api_headers,
        )

        response.raise_for_status()  # Raise an error for bad responses

        return response.text


@mcp.tool(
    name="search_webkr",
    description="Search web pages on Naver",
)
def search_webkr(
    query: str,
    display: int = 10,
    start: int = 1,
):
    """
    네이버 검색의 웹 문서 검색 결과를 반환합니다.
    일반 웹페이지, 홈페이지, 기업 사이트 등의 웹 콘텐츠를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
        display (int, optional): 한 번에 표시할 검색 결과 개수 (기본값: 10, 최대: 100)
        start (int, optional): 검색 시작 위치 (기본값: 1, 최대: 1000)
    """

    with httpx.Client() as client:
        response = client.get(
            f"{API_ENDPOINT}/search/webkr.json",
            params={
                "query": query,
                "display": display,
                "start": start,
            },
            headers=api_headers,
        )

        response.raise_for_status()  # Raise an error for bad responses

        return response.text


if __name__ == "__main__":
    mcp.run()
