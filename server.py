# demo.py
import json
import os

import httpx
import xmltodict
from fastmcp import FastMCP

import requests
from typing import Annotated, List


mcp = FastMCP("Naver OpenAPI", dependencies=["httpx", "xmltodict"])

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
NAVER_API_HEADERS = {
    "X-Naver-Client-Id": NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
}
NAVER_API_ENDPOINT = "https://openapi.naver.com/v1"

# Google Custom Search API 설정
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
GOOGLE_BASE_URL = "https://www.googleapis.com/customsearch/v1"

# Youtube MCP API 설정
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

# Kakao API 설정
KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY")
KAKAO_API_HEADERS = {
    "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}",
    "Content-Type" : "application/json",
}
KAKAO_LOCAL_API_ENDPOINT = "https://dapi.kakao.com"
KAKAO_NAVI_API_ENDPOINT = "https://apis-navi.kakaomobility.com"


# Based on code from mcp-naver by pfldy2850 (MIT License)
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

# Based on code from mcp-naver by pfldy2850 (MIT License)
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

# Based on code from mcp-naver by pfldy2850 (MIT License)
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


@mcp.tool(
    name="search_google",
    description="Search web pages using Google Custom Search API",
)
def search_google(
    query: str,
    num_results: int = 10,
    start_index: int = 1,
    search_type: str = None,
    language: str = "ko",
):
    """
    Google Custom Search API를 사용하여 웹 검색을 수행합니다.
    웹페이지, 이미지, 뉴스 등 다양한 콘텐츠를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
        num_results (int, optional): 결과 개수 (기본값: 10, 최대: 10)
        start_index (int, optional): 시작 인덱스 (페이지네이션용, 기본값: 1)
        search_type (str, optional): 검색 타입 - "image" (이미지 검색), None (웹 검색)
        language (str, optional): 검색 언어 - "ko" (한국어), "en" (영어) 등 (기본값: "ko")
    """
    
    if not GOOGLE_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
        return json.dumps({
            "error": "Google API 키 또는 검색 엔진 ID가 설정되지 않았습니다. GOOGLE_API_KEY와 GOOGLE_SEARCH_ENGINE_ID 환경 변수를 확인해주세요."
        })

    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_SEARCH_ENGINE_ID,
        'q': query,
        'num': min(num_results, 10),  # 최대 10개
        'start': start_index,
        'hl': language,  # 인터페이스 언어
        'lr': f'lang_{language}',  # 검색 결과 언어
    }
    
    # 이미지 검색인 경우 searchType 파라미터 추가
    if search_type == "image":
        params['searchType'] = 'image'
    
    try:
        with httpx.Client() as client:
            response = client.get(GOOGLE_BASE_URL, params=params)
            response.raise_for_status()
            return response.text
    
    except httpx.HTTPStatusError as e:
        error_msg = f"Google API 요청 오류: {e.response.status_code} - {e.response.text}"
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Google 검색 중 오류 발생: {str(e)}"
        return json.dumps({"error": error_msg})

### 유튜브 MCP 서비스 ###
@mcp.tool(
    name="search_video",
    description="Search for a YouTube video",
)

async def search_video(
    query: str,
    max_results: int = 10,
):
    """
    Search for a YouTube video

    Args:
        query (str): The query to search for.
        max_results (int, optional): The maximum number of results to return. Defaults to 10.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={YOUTUBE_API_KEY}",
            params={
                "part": "snippet",
                "q": query,
                "key": YOUTUBE_API_KEY,
            },
            headers=api_headers,
        )   

        response.raise_for_status() 

        return response.text


@mcp.tool(
    name="get_video_details",
    description="Get the details of a YouTube video",
)

async def get_video_details(
    video_id: str
):
    """
    Get the details of a YouTube video

    Args:
        video_id (str): The ID of the YouTube video
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}",
            params={
                "part": "snippet",
                "id": video_id,
                "key": YOUTUBE_API_KEY,
            },
            headers=api_headers,
        )

        response.raise_for_status()

        return response.text


@mcp.tool(
    name="get_youtube_transcript",
    description="Get the transcript of a YouTube video",
)

async def get_youtube_transcript(
    video_id: str
):

    """
    Get the transcript of a YouTube video
    
    Args:
        video_id (str): The ID of the YouTube video
    """

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}",
            params={
                "part": "snippet",
                "id": video_id,
                "key": YOUTUBE_API_KEY,
            },
            headers=api_headers,
        )

        response.raise_for_status()

        return response.text



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


def find_route_kakao(
    origin : Annotated[str, "출발지의 이름"],
    destination : Annotated[str, "도착지의 이름"],
    way_points : Annotated[List[str], "출발지의 이름"] = [],
    priority : Annotated[str, "탐색 우선 순위 옵션"] = 'RECOMMEND',
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
    return response

@mcp.tool(
    name="mcp_search_local_kakao",
    description="Search local information on Kakao",
)
def mcp_search_local_kakao(
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
    name="mcp_search_webkr_kakao",
    description="Search web pages on Kakao",
)
def mcp_search_webkr_kakao(
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



@mcp.tool(
    name="mcp_find_route_kakao",
    description="이동 경로상 경유지 정보를 반환합니다."
    )
def mcp_find_route_kakao(
    origin : Annotated[str, "출발지의 이름"],
    destination : Annotated[str, "도착지의 이름"],
    way_points : Annotated[List[str], "경유지의 이름"] = [],
    priority : Annotated[str, "탐색 우선 순위 옵션"] = 'RECOMMEND',
    ):
    """
    출발지, 목적지와 경유지를 입력하면 좌표로 변환 후
    이동 경로상 경유지 정보를 반환합니다.
    

    Args:
        origin (str) : 출발지의 이름
        destination (str) : 도착지의 이름
        way_points (str) : 경유지의 이름
        priority (str) : 경로 우선 순위 옵션
                RECOMMEND : 추천 경로
                TIME      : 최단 시간
                DISTANCE  : 최단 경로
    """
    response = find_route_kakao(origin, destination, way_points, priority)
    data = response.json()
    road_section = data['routes'][0]['sections'][0]['roads']

    refined_road_section = []
    
    last_road_name = None
    for road in road_section:
        if last_road_name != road['name']:
            last_road_name = road['name']
            refined_road_section.append({'name':last_road_name,
                                         'vertexes': [(road['vertexes'][0],road['vertexes'][1]),None]})
                        
        refined_road_section[-1]['vertexes'][-1] = (road['vertexes'][-2],road['vertexes'][-1])
    data['routes'][0]['sections'][0]['roads'] = refined_road_section
    
    return str(data)

if __name__ == "__main__":
    mcp.run()
