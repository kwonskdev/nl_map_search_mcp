import json
import os
from typing import Any, Dict, List

import httpx


KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY")
KAKAO_API_HEADERS = {
    "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}",
    "Content-Type": "application/json",
}
KAKAO_LOCAL_API_ENDPOINT = "https://dapi.kakao.com"
KAKAO_NAVI_API_ENDPOINT = "https://apis-navi.kakaomobility.com"


async def search_local_kakao(
    query: str
) -> str:
    """
    카카오 지역 서비스에 등록된 지역별 업체 및 상호 검색 결과를 반환합니다.
    음식점, 카페, 병원, 약국, 편의점 등 지역 기반 업체 정보를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구

    Returns:
        str: 검색 결과 JSON 문자열
    """
    url = f"{KAKAO_LOCAL_API_ENDPOINT}/v2/local/search/keyword.json"
    params = {"query": query}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=KAKAO_API_HEADERS, params=params)
        response.raise_for_status()
        return response.text


async def search_web_kakao(
    query: str
) -> str:
    """
    카카오 검색의 웹 문서 검색 결과를 반환합니다.
    일반 웹페이지, 홈페이지, 기업 사이트 등의 웹 콘텐츠를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구

    Returns:
        str: 검색 결과 JSON 문자열
    """
    url = f"{KAKAO_LOCAL_API_ENDPOINT}/v2/search/web"
    params = {"query": query}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=KAKAO_API_HEADERS, params=params)
        response.raise_for_status()
        return response.text


async def get_coordinates(
    destination: str
) -> Dict[str, Any]:
    """
    장소명을 입력받아 해당 위치의 좌표를 반환합니다.

    Args:
        destination (str): 좌표를 구할 장소명

    Returns:
        Dict[str, Any]: 장소명과 x, y 좌표가 포함된 딕셔너리
    """
    response_text = await search_local_kakao(destination)
    data = json.loads(response_text)["documents"][0]
    return {
        "name": destination, 
        "x": data["x"], 
        "y": data["y"]
    }


async def find_route_kakao(
    origin: str,
    destination: str,
    way_points: List[str] = None,
    priority: str = "RECOMMEND"
) -> str:
    """
    출발지, 목적지와 경유지를 입력하면 좌표로 변환 후
    카카오 네비를 통하여 경유지를 포함한 경로 정보를 반환합니다.

    Args:
        origin (str): 출발지의 이름
        destination (str): 도착지의 이름
        way_points (List[str], optional): 경유지의 이름 목록
        priority (str): 경로 우선 순위 옵션
            - RECOMMEND: 추천 경로
            - TIME: 최단 시간
            - DISTANCE: 최단 경로

    Returns:
        str: 경로 정보 JSON 문자열
    """
    if way_points is None:
        way_points = []
        
    url = f"{KAKAO_NAVI_API_ENDPOINT}/v1/waypoints/directions"
    
    origin_info = await get_coordinates(origin)
    destination_info = await get_coordinates(destination)
    way_points_info = []
    for way_point in way_points:
        coordinate = await get_coordinates(way_point)
        way_points_info.append(coordinate)
    
    data = {
        "origin": origin_info,
        "destination": destination_info,
        "waypoints": way_points_info,
        "priority": priority,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=KAKAO_API_HEADERS, json=data)
        response.raise_for_status()
        return response.text


async def get_refined_route_info(
    origin: str,
    destination: str,
    way_points: List[str] = None,
    priority: str = "RECOMMEND"
) -> str:
    """
    경로 정보를 가져와서 도로 구간 정보를 정제하여 반환합니다.

    Args:
        origin (str): 출발지의 이름
        destination (str): 도착지의 이름
        way_points (List[str], optional): 경유지의 이름 목록
        priority (str): 경로 우선 순위 옵션

    Returns:
        str: 정제된 경로 정보 문자열
    """
    response_text = await find_route_kakao(
        origin, destination, way_points, priority
    )
    data = json.loads(response_text)
    road_section = data["routes"][0]["sections"][0]["roads"]

    refined_road_section = []
    last_road_name = None
    
    for road in road_section:
        if last_road_name != road["name"]:
            last_road_name = road["name"]
            refined_road_section.append({
                "name": last_road_name,
                "vertexes": [
                    (road["vertexes"][0], road["vertexes"][1]), 
                    None
                ]
            })
        
        refined_road_section[-1]["vertexes"][-1] = (
            road["vertexes"][-2], 
            road["vertexes"][-1]
        )
    
    data["routes"][0]["sections"][0]["roads"] = refined_road_section
    return str(data)