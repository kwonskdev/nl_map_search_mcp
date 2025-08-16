## Attribution

This project uses code from mcp-naver by pfldy2850, licensed under the MIT License.
Original project: https://github.com/pfldy2850/py-mcp-naver.git

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Multi-Platform Search MCP Server

다중 플랫폼 검색 기능을 제공하는 MCP (Model Context Protocol) 서버입니다. 네이버, 카카오, 구글, 유튜브 등 여러 플랫폼의 검색 API를 통합하여 제공합니다.

## 🚀 주요 기능

### 검색 도구 (Search Tools)

#### 1. `search_web` - 일반 웹 검색
- **용도**: 가장 일반적인 웹 검색 도구
- **플랫폼**: Naver, Kakao, Google
- **특징**: 종합적인 검색 결과, 뉴스, 기사, 일반 웹 콘텐츠
- **사용 시점**: 광범위한 정보 수집이 필요할 때

#### 2. `search_review` - 리뷰 및 경험담 검색
- **용도**: 사용자 리뷰, 의견, 경험담 검색
- **플랫폼**: Naver 블로그, YouTube 동영상
- **특징**: 개인적인 리뷰와 주관적인 의견, YouTube 동영상 상세 정보 및 자막 포함
- **사용 시점**: 제품, 서비스, 장소에 대한 구체적인 리뷰가 필요할 때

#### 3. `search_local` - 업체 정보 검색
- **용도**: 공식 업체 정보 검색
- **플랫폼**: Naver, Kakao
- **특징**: 전화번호, 주소, 영업시간, 업체 카테고리 등 공식 정보
- **사용 시점**: 음식점, 카페, 병원 등의 정확한 업체 정보가 필요할 때

#### 4. `find_route_with_stops` - 경유지 포함 경로 검색
- **용도**: 경유지가 포함된 최적 경로 탐색
- **플랫폼**: Kakao 네비 API
- **특징**: 출발지, 도착지, 경유지 설정 및 경로 우선순위 설정
- **사용 시점**: 여행 중 주유소, 휴게소 등 특정 장소를 경유해야 할 때

## 📁 프로젝트 구조

```
nl_map_search_mcp/
├── server.py              # MCP 서버 및 도구 정의
├── apis/                   # API 모듈들
│   ├── __init__.py
│   ├── naver.py           # 네이버 API 기능
│   ├── kakao.py           # 카카오 API 기능
│   ├── youtube.py         # 유튜브 API 기능
│   └── google.py          # 구글 API 기능
└── README.md
```

## 🔧 설치 및 설정

### 1. 저장소 클론 및 의존성 설치

```bash
# 저장소 클론
git clone https://github.com/kwonskdev/nl_map_search_mcp.git 

# 프로젝트 디렉토리로 이동
cd nl_map_search_mcp

# 의존성 동기화
uv sync --dev --all-extras
```

### 2. 환경 변수 설정

.env 파일을 생성하고 다음 API 키들을 설정해야 합니다:

```bash
# Naver API
NAVER_CLIENT_ID=<YOUR NAVER CLIENT ID>
NAVER_CLIENT_SECRET=<YOUR NAVER CLIENT SECRET>

# Kakao API
KAKAO_REST_API_KEY=<YOUR KAKAO REST API KEY>

# YouTube API
YOUTUBE_API_KEY=<YOUR YOUTUBE API KEY>

# Google Custom Search API
GOOGLE_API_KEY=<YOUR GOOGLE API KEY>
GOOGLE_SEARCH_ENGINE_ID=<YOUR SEARCH ENGINE ID>
```

### 3. 서버 실행

```powershell
uv run fastmcp install cursor nl_map_search_mcp/server.py --env-file .env
```

## 🔑 API 키 획득 방법

### Naver API
- [Naver Developers](https://developers.naver.com/) 에서 애플리케이션 등록
- 검색 API 사용 권한 신청
- Client ID와 Client Secret 획득

### Kakao API
- [Kakao Developers](https://developers.kakao.com/) 에서 앱 생성
- 로컬 API와 네비 API 사용 권한 활성화
- REST API 키 획득

### YouTube API
- [Google Cloud Console](https://console.cloud.google.com/) 에서 프로젝트 생성
- YouTube Data API v3 활성화
- API 키 생성

### Google Custom Search API
- [Google Cloud Console](https://console.cloud.google.com/) 에서 Custom Search API 활성화
- [Programmable Search Engine](https://programmablesearchengine.google.com/) 에서 검색엔진 생성
- API 키와 검색엔진 ID 획득

<details>
<summary>📖 Naver MCP Server (기존 README 내용 보기)</summary>

# Naver MCP Server

A server implementation for Naver OpenAPI using the Model Context Protocol (MCP). This project provides tools to interact with various Naver services, such as searching blogs, news, books, and more.

## Pre-requisite
To use the Naver MCP server, you need to apply for access to the Naver Open API.  
You can apply for Open API access at the link below:

https://developers.naver.com/apps/#/register=datalab

## Installation

### from PyPi (Claude Desktop)
Install it to Claude Desktop with (uv):
```sh
uv pip install mcp-naver

uv run python -m mcp-naver.hosts.claude_desktop \
  -e NAVER_CLIENT_ID=<YOUR NAVER CLIENT ID> \
  -e NAVER_CLIENT_SECRET=<YOUR NAVER CLIENT SECRET>
```

Install it to Claude Desktop with:
```sh
pip install mcp-naver

python -m mcp-naver.hosts.claude_desktop \
  -e NAVER_CLIENT_ID=<YOUR NAVER CLIENT ID> \
  -e NAVER_CLIENT_SECRET=<YOUR NAVER CLIENT SECRET>
```

### from PyPi (Cursor)
Install it to Cursor with (uv):
```sh
uv pip install mcp-naver

uv run python -m mcp-naver.hosts.cursor \
  -e NAVER_CLIENT_ID=<YOUR NAVER CLIENT ID> \
  -e NAVER_CLIENT_SECRET=<YOUR NAVER_CLIENT_SECRET>
```

### from source
```sh
# Clone the repository
git clone https://github.com/pfldy2850/py-mcp-naver.git

# Navigate into the project directory
cd py-mcp-naver

# Synchronize dependencies
uv sync --dev --all-extras
```

Run it with:
```sh
# Start the server (Using FastMCP CLI)
fastmcp install mcp_naver/server.py \
  -e NAVER_CLIENT_ID=<YOUR NAVER CLIENT ID> \
  -e NAVER_CLIENT_SECRET=<YOUR NAVER CLIENT SECRET>
```

## Features

- **Blog Search**: Search blog posts on Naver.
- **News Search**: Search news articles on Naver.
- **Book Search**: Search books and advanced book information.
- **Adult Content Check**: Check if a search term is adult content.
- **Encyclopedia Search**: Search encyclopedia entries.
- **Cafe Article Search**: Search articles in Naver cafes.
- **Q&A Search**: Search questions and answers on Naver.
- **Local Search**: Search local information.
- **Spelling Correction**: Correct spelling errors in text.
- **Web Search**: Search web pages.
- **Image Search**: Search images with filters.
- **Shopping Search**: Search shopping items with filters.
- **Document Search**: Search documents.

## Naver MCP Tools

### Blog Search
```python
search_blog(query: str, display: int = 10, start: int = 1, sort: str = "sim")
```

### News Search
```python
search_news(query: str, display: int = 10, start: int = 1, sort: str = "sim")
```

### Book Search
```python
search_book(query: str, display: int = 10, start: int = 1, sort: str = "sim")
```

### Advanced Book Search
```python
get_book_adv(query: str = None, d_titl: str = None, d_isbn: str = None, ...)
```

### Adult Content Check
```python
adult_check(query: str)
```

### Encyclopedia Search
```python
search_encyc(query: str, display: int = 10, start: int = 1)
```

### Cafe Article Search
```python
search_cafe_article(query: str, display: int = 10, start: int = 1, sort: str = "sim")
```

### Q&A Search
```python
search_kin(query: str, display: int = 10, start: int = 1, sort: str = "sim")
```

### Local Search
```python
search_local(query: str, display: int = 10, start: int = 1, sort: str = "random")
```

### Spelling Correction
```python
fix_spelling(query: str)
```

### Web Search
```python
search_webkr(query: str, display: int = 10, start: int = 1)
```

### Image Search
```python
search_image(query: str, display: int = 10, start: int = 1, sort: str = "sim", filter: str = "all")
```

### Shopping Search
```python
search_shop(query: str, display: int = 10, start: int = 1, sort: str = "sim", filter: str = None, exclude: str = None)
```

### Document Search
```python
search_doc(query: str, display: int = 10, start: int = 1)
```

## License

This project is open source software [licensed as MIT](https://opensource.org/licenses/MIT).

</details>
