from typing import Dict, Annotated, List, Optional
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import distance as geopy_distance
import webbrowser
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import os


from apis import kakao
# 환경변수로 사용자 에이전트 설정 권장
NOMINATIM_USER_AGENT = os.environ.get("NOMINATIM_USER_AGENT", "mcp-geocoder-example")
_geolocator = Nominatim(user_agent=NOMINATIM_USER_AGENT, timeout=10)

# 내부 쓰레드풀(geopy는 블로킹이므로 비동기 함수에서 run_in_executor로 사용)
_thread_executor = ThreadPoolExecutor(max_workers=4)

def _within_radius(center: Dict[str,float], point: Dict[str,float], radius_m: float) -> bool:
    """center and point: {'lat':..., 'lon':...}"""
    return geopy_distance((center['lat'], center['lon']), (point['lat'], point['lon'])).meters <= radius_m

async def places_to_map(
    places: Annotated[List[str], "검색할 장소 이름 리스트"],
    center: Optional[Dict[str, float]] = None,
    radius_m: Optional[float] = None,
    map_title: str = "Places Map",
    zoom_start: int = 15,
    save_to: Optional[str] = None,  # optional output filepath; if None, saves to /tmp
    cluster_markers: bool = True,
    html_only: bool = False,  # if True, return only HTML content without saving file
) -> str:
    """
    places: list of dicts, each dict may have:
      - name (required)
      - address (optional)
      - lat (optional)
      - lon (optional)
      - popup (optional)  # html/text for popup
    center: {'lat': .., 'lon': ..} optional - map center and for radius filter
    radius_m: if provided, only include places within radius_m meters of center
    Returns: HTML string of the map (and also saves file under save_to or temp file).
    """

    # 1) geocode missing coords (with polite delay)
    resolved_places = []
    for p in places:
        
        p_info = json.loads(await kakao.search_local_kakao(p))['documents'][0]
        lat = p_info['y']
        lon = p_info['x']
        
        candidate = {"name": p, "lat": float(lat), "lon": float(lon), "popup": ""}
        # optional original metadata
        candidate["meta"] = p
        resolved_places.append(candidate)
        # rate-limit politeness
        await asyncio.sleep(0.2)

    # 2) optional radius filter
    if center and radius_m:
        filtered = [pl for pl in resolved_places if _within_radius(center, {"lat":pl["lat"], "lon":pl["lon"]}, radius_m)]
    else:
        filtered = resolved_places

    if not filtered:
        return json.dumps({"error": "No resolvable places within constraints."}, ensure_ascii=False)

    # 3) build folium map
    map_center = (center["lat"], center["lon"]) if center else (filtered[0]["lat"], filtered[0]["lon"])
    fmap = folium.Map(location=map_center, zoom_start=zoom_start, control_scale=True)
    if cluster_markers:
        marker_cluster = MarkerCluster().add_to(fmap)
    else:
        marker_cluster = None

    for pl in filtered:
        popup_html = f"<b>{pl['name']}</b><br/>{pl.get('popup','')}"
        marker = folium.Marker(location=(pl["lat"], pl["lon"]), popup=folium.Popup(popup_html, max_width=300))
        if marker_cluster:
            marker.add_to(marker_cluster)
        else:
            marker.add_to(fmap)

    # 4) save HTML to file and also return HTML string
    if html_only:
        # return only HTML content without saving file
        return fmap._repr_html_()
    
    # 현재 파일의 디렉토리를 기준으로 maps 폴더 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    maps_dir = os.path.join(current_dir, "..", "maps")
    os.makedirs(maps_dir, exist_ok=True)
    
    if not save_to:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        save_to = os.path.join(maps_dir, f"map_{timestamp}.html")
    else:
        # save_to가 상대 경로인 경우 maps 폴더 기준으로 절대 경로로 변환
        if not os.path.isabs(save_to):
            save_to = os.path.join(maps_dir, save_to)

    fmap.save(save_to)

    # 파일명만 추출 (경로에서)
    filename = os.path.basename(save_to)
    
    # 자동으로 브라우저에서 열기 시도
    try:
        webbrowser.open(f"file://{save_to}")
        browser_opened = True
    except Exception:
        browser_opened = False
    
    # HTML 링크가 포함된 응답 생성
    response_text = f"""지도가 성공적으로 생성되었습니다!

📍 **생성된 지도**: [{filename}](file://{save_to})

{'✅ 브라우저에서 자동으로 열렸습니다!' if browser_opened else '💡 지도 파일을 클릭하시면 브라우저에서 열립니다.'}

만약 클릭이 안 되시면 아래 경로를 복사해서 브라우저 주소창에 붙여넣어주세요:

`file://{save_to}`

**지도 정보:**
- 총 {len(filtered)}개 장소 표시
- 중심점: {map_center[0]:.6f}, {map_center[1]:.6f}
- 줌 레벨: {zoom_start}
- 마커 클러스터링: {'활성화' if cluster_markers else '비활성화'}

지도에서 각 마커를 클릭하면 장소 정보를 확인할 수 있습니다."""

    return response_text