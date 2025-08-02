# demo.py
import json
import os
import requests
import httpx
import xmltodict
from fastmcp import FastMCP

mcp = FastMCP("Kakao OpenAPI", dependencies=["httpx", "xmltodict"])

KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY")

KAKAO_API_HEADERS = {
    "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}",
}

KAKAO_LOCAL_API_ENDPOINT = "https://dapi.kakao.com"
KAKAO_NAVI_API_ENDPOINT = "https://apis-navi.kakaomobility.com"


@mcp.tool(
    name="search_local_kakao",
    description="Search local information on Kakao",
)
def search_local_kakao(
    query: str,
):
    """
    카카오 지역 서비스에 등록된 지역별 업체 및 상호 검색 결과를 반환합니다.
    음식점, 카페, 병원, 약국, 편의점 등 지역 기반 업체 정보를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
    """
    url = f"{KAKAO_LOCAL_API_ENDPOINT}/v2/local/search/keyword.json"
    headers = KAKAO_API_HEADERS
    params = {'query' : query}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.text
    data = response.json()['documents']
    return data


@mcp.tool(
    name="search_webkr_kakao",
    description="Search web pages on Kakao",
)
def search_webkr_kakao(
    query: str,
):
    """
    카카오 검색의 웹 문서 검색 결과를 반환합니다.
    일반 웹페이지, 홈페이지, 기업 사이트 등의 웹 콘텐츠를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
    """

    url = f"{KAKAO_LOCAL_API_ENDPOINT}/v2/search/web"
    headers = KAKAO_API_HEADERS
    params = {'query' : query}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.text
    data = response.json()['documents']
    return data


if __name__ == "__main__":
    mcp.run()
