import json
from typing import Annotated, List

from fastmcp import FastMCP

from apis import google, kakao, naver, youtube


mcp = FastMCP("Multi-Platform Search API", dependencies=["httpx"])


@mcp.tool(
    name="search_review",
    description="Find user reviews, opinions, and experiences from Naver blogs and YouTube videos. Use when you need personal reviews, detailed experiences, or subjective opinions about products, services, or places.",
)
async def search_review(
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "sim",
    sites: List[str] = ["naver", "youtube"],
):
    """
    네이버 블로그 포스트와 YouTube 동영상을 검색합니다.
    YouTube 검색 시 동영상 상세 정보와 자막 정보도 함께 포함됩니다.

    Args:
        query (str): 검색할 키워드나 문구
        display (int): 한 번에 표시할 검색 결과 개수 (기본값: 10, 최대: 100)
        start (int): 검색 시작 위치 (기본값: 1, 최대: 1000)
        sort (str): 정렬 방법 - "sim"(정확도순), "date"(최신순) (기본값: "sim")
        sites (List[str]): 검색할 사이트 목록 ["naver", "youtube"]

    Returns:
        str: 검색 결과 JSON 문자열
    """
    response_parts = []

    if "naver" in sites:
        naver_result = await naver.search_blog_naver(query, display, start, sort)
        response_parts.append(f"Naver: {naver_result}")

    if "youtube" in sites:
        youtube_result = await youtube.search_videos_youtube(query, display)
        response_parts.append(f"Youtube: {json.dumps(youtube_result, ensure_ascii=False, indent=4)}")

    return "\n".join(response_parts)

@mcp.tool(
    name="search_local",
    description="Find official business information including phone numbers, addresses, business hours, and categories from Naver and Kakao. Use when you need factual business details rather than user reviews.",
)
async def search_local(
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = "random",
    sites: List[str] = ["naver", "kakao"]
):
    """
    네이버와 카카오 지역 서비스에서 지역별 업체 및 상호를 검색합니다.
    음식점, 카페, 병원, 약국, 편의점 등 지역 기반 업체 정보를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
        display (int): 한 번에 표시할 검색 결과 개수 (기본값: 10, 최대: 100)
        start (int): 검색 시작 위치 (기본값: 1, 최대: 1000)
        sort (str): 정렬 방법 - "random"(랜덤순), "comment"(리뷰순), "count"(방문자순)
        sites (List[str]): 검색할 사이트 목록 ["naver", "kakao"]

    Returns:
        str: 지역 검색 결과 JSON 문자열
    """
    response_parts = []

    if "naver" in sites:
        naver_result = await naver.search_local_naver(query, display, start, sort)
        response_parts.append(f"Naver: {naver_result}")

    if "kakao" in sites:
        kakao_result = await kakao.search_local_kakao(query)
        response_parts.append(f"Kakao: {kakao_result}")

    return "\n".join(response_parts)

@mcp.tool(
    name="search_web",
    description="General web search across multiple platforms (Naver, Kakao, Google). Use for broad information gathering, news, articles, and general web content when you need comprehensive search results.",
)
async def search_web(
    query: str,
    display: int = 10,
    start: int = 1,
    sites: List[str] = ["naver", "kakao", "google"],
):
    """
    네이버, 카카오, 구글에서 웹 문서를 검색합니다.
    일반 웹페이지, 홈페이지, 기업 사이트 등의 웹 콘텐츠를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
        display (int): 한 번에 표시할 검색 결과 개수 (기본값: 10, 최대: 100)
        start (int): 검색 시작 위치 (기본값: 1, 최대: 1000)
        sites (List[str]): 검색할 사이트 목록 ["naver", "kakao", "google"]

    Returns:
        str: 웹 검색 결과 JSON 문자열
    """
    response_parts = []

    if "naver" in sites:
        naver_result = await naver.search_web_naver(query, display, start)
        response_parts.append(f"Naver: {naver_result}")

    if "kakao" in sites:
        kakao_result = await kakao.search_web_kakao(query)
        response_parts.append(f"Kakao: {kakao_result}")

    if "google" in sites:
        google_result = await google.search_web_google(query, display, start)
        response_parts.append(f"Google: {google_result}")

    return "\n".join(response_parts)

@mcp.tool(
    name="search_route_stops",
    description="Search for specific locations along your current route or planned journey. Use when you're already traveling from A to B and need to find places like gas stations, rest areas, or other points of interest along the way.",
)
async def search_route_stops(
    origin: Annotated[str, "출발지의 이름"],
    destination: Annotated[str, "도착지의 이름"],
    way_points: Annotated[List[str], "경유지의 이름"] = None,
    priority: Annotated[str, "탐색 우선 순위 옵션"] = "RECOMMEND"
):
    """
    출발지, 목적지와 경유지를 입력하면 좌표로 변환 후
    카카오 네비를 통하여 경유지를 포함한 정제된 경로 정보를 반환합니다.

    Args:
        origin (str): 출발지의 이름
        destination (str): 도착지의 이름
        way_points (List[str], optional): 경유지의 이름 목록
        priority (str): 경로 우선 순위 옵션
            - RECOMMEND: 추천 경로
            - TIME: 최단 시간
            - DISTANCE: 최단 경로

    Returns:
        str: 정제된 경로 정보 문자열
    """
    if way_points is None:
        way_points = []
        
    return await kakao.get_refined_route_info(origin, destination, way_points, priority)

if __name__ == "__main__":
    mcp.run()
