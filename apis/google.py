import os
from typing import Any, Dict

import httpx


GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
GOOGLE_BASE_URL = "https://www.googleapis.com/customsearch/v1"


async def search_web_google(
    query: str,
    display: int = 10,
    start: int = 1
) -> str:
    """
    Google Custom Search API를 사용하여 웹 검색 결과를 반환합니다.
    일반 웹페이지, 홈페이지, 기업 사이트 등의 웹 콘텐츠를 검색할 수 있습니다.

    Args:
        query (str): 검색할 키워드나 문구
        display (int): 한 번에 표시할 검색 결과 개수 (기본값: 10, 최대: 10)
        start (int): 검색 시작 위치 (기본값: 1)

    Returns:
        str: Google 검색 결과 JSON 문자열
    """
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_SEARCH_ENGINE_ID,
        "q": query,
        "num": display,
        "start": start,
        "hl": "ko",
        "lr": "lang_ko",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(GOOGLE_BASE_URL, params=params)
        response.raise_for_status()
        return response.text