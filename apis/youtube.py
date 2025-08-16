import json
import os
from typing import Any, Dict

import httpx


YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")


async def search_videos_youtube(
    query: str,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    YouTube에서 동영상을 검색하고 상세 정보와 자막을 포함하여 반환합니다.

    Args:
        query (str): 검색할 키워드나 문구
        max_results (int): 검색 결과 개수 (기본값: 10)

    Returns:
        Dict[str, Any]: 동영상 검색 결과와 상세 정보가 포함된 딕셔너리
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": query,
                "key": YOUTUBE_API_KEY,
                "maxResults": max_results,
                "type": "video"
            }
        )
        response.raise_for_status()
        
        search_data = response.json()
        
        if "items" in search_data:
            for video in search_data["items"]:
                if "videoId" in video["id"]:
                    video_id = video["id"]["videoId"]
                    
                    video_details = await get_video_details(video_id)
                    video["detail"] = video_details
                    
                    video_transcript = await get_youtube_transcript(video_id)
                    video["transcript"] = video_transcript
        
        return search_data


async def get_video_details(
    video_id: str
) -> str:
    """
    YouTube 동영상의 상세 정보를 가져옵니다.

    Args:
        video_id (str): YouTube 동영상 ID

    Returns:
        str: 동영상 상세 정보 JSON 문자열
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,statistics,contentDetails",
                "id": video_id,
                "key": YOUTUBE_API_KEY,
            }
        )
        response.raise_for_status()
        return response.text


async def get_youtube_transcript(
    video_id: str
) -> str:
    """
    YouTube 동영상의 자막을 가져옵니다.
    현재는 placeholder 함수로, 실제 자막 API가 필요한 경우 youtube-transcript-api 등을 사용해야 합니다.

    Args:
        video_id (str): YouTube 동영상 ID

    Returns:
        str: 자막 정보 (현재는 placeholder)
    """
    # TODO: 실제 자막 API 구현 필요 (youtube-transcript-api 등 사용)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet",
                "id": video_id,
                "key": YOUTUBE_API_KEY,
            }
        )
        response.raise_for_status()
        return response.text