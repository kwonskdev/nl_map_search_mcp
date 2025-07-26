# nl_map_search_mcp
자연어로 지도에서 장소 검색하는 MCP 서버

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
  -e NAVER_CLIENT_SECRET=<YOUR NAVER CLIENT_SECRET>
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
