# demo.py
import json
import os
import requests
import httpx
import xmltodict
from fastmcp import FastMCP
from typing import Annotated, List

mcp = FastMCP("Kakao OpenAPI", dependencies=["httpx", "xmltodict"])

KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY")
KAKAO_REST_API_KEY = '0dcef6597717e7675a680b6bdfd18016'
KAKAO_API_HEADERS = {
    "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}",
    "Content-Type" : "application/json",
}

KAKAO_LOCAL_API_ENDPOINT = "https://dapi.kakao.com"
KAKAO_NAVI_API_ENDPOINT = "https://apis-navi.kakaomobility.com"


def search_local_kakao_response(
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
    return response

def get_coord(
    destination: str,
    ):
    res = search_local_kakao_response(destination)
    data = res.json()['documents'][0]
    return {'name':destination, 'x':data['x'], 'y':data['y']}

@mcp.tool(
    name="search_local_kakao",
    description="Search local information on Kakao",
)
def search_local_kakao(
    query: Annotated[str, "검색할 키워드를 입력하세요."],
):
    """
    카카오 지역 서비스에 등록된 지역별 업체 및 상호 검색 결과를 반환합니다.
    음식점, 카페, 병원, 약국, 편의점 등 지역 기반 업체 정보를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
    """
    response = search_local_kakao_response(query)
    return response.text


@mcp.tool(
    name="search_webkr_kakao",
    description="Search web pages on Kakao",
)
def search_webkr_kakao(
    query: Annotated[str, "검색할 키워드를 입력하세요."],
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


@mcp.tool(
    name="find_route_kakao",
    description="get coord and Search route on Kakao Navi "
    )
def find_route_kakao(
    origin : Annotated[str, "출발지의 이름"],
    destination : Annotated[str, "도착지의 이름"],
    way_points : Annotated[List[str], "출발지의 이름"],
    priority : Annotated[str, "탐색 우선 순위 옵션"],
    ):
    """
    목적지와 경유지를 입력하면 좌표로 변환 후
    카카오 네비를 통하여 경유지를 포함한 경로 정보를 반환합니다.

    Args:
        origin (str) : 출발지의 이름
        destination (str) : 도착지의 이름
        way_points (str) : 경유지의 이름
        priority (str) : 경로 우선 순위 옵션
                RECOMMEND : 추천 경로
                TIME      : 최단 시간
                DISTANCE  : 최단 경로
    """
    url = f"{KAKAO_NAVI_API_ENDPOINT}/v1/waypoints/directions"
    headers = KAKAO_API_HEADERS

    
    origin_info = get_coord(origin)
    destination_info = get_coord(destination)
    way_points_info = [get_coord(way_point) for way_point in way_points]

    data = {
        "origin":origin_info,
        "destination":destination_info,
        "waypoints":way_points_info,
        "priority":priority,
        }
    response = requests.post(url, headers=headers, json=data)
    return response.text
    
if __name__ == "__main__":
    mcp.run()
