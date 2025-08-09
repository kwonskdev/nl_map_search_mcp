# MCP Web Client

MCP (Model Context Protocol) 웹 클라이언트로, 브라우저에서 MCP 서버에 연결하여 도구를 사용할 수 있습니다.

## 설정 파일

`.mcp.json.example`을 참고해서 `.mcp.json` 파일을 생성하여 연결할 서버들을 설정합니다:

```json
{
  "mcpServers": {
    "naver-openapi": {
      "command": "uv",
      "args": ["--directory", "../server", "run", "mcp_naver/server.py"],
      "env": {
        "NAVER_CLIENT_ID": "your_naver_client_id",
        "NAVER_CLIENT_SECRET": "your_naver_client_secret"
      }
    },
    "js-server": {
      "command": "node",
      "args": ["/path/to/server.js"],
      "env": {
        "NODE_ENV": "production"
      }
    },
    "npm-server": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-everything"],
      "env": {}
    },
    "executable-server": {
      "command": "/usr/local/bin/my-server",
      "args": ["--config", "config.json"],
      "env": {
        "API_KEY": "secret-key"
      }
    },
    "example-test-server": {
      "command": "echo",
      "args": ["This is just an example"],
      "env": {}
    }
  }
}
```

> **참고**: `example`로 시작하는 서버들은 자동으로 제외됩니다.

## 환경 변수

`.env` 파일에 필요한 환경 변수를 설정하세요:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## 사용법

### 웹 인터페이스 (권장)

```bash
# 웹 클라이언트 실행
uv run client.py
```

그 후 브라우저에서 `http://localhost:8080` 접속

### 기능

- **자동 서버 연결**: 웹 시작 시 `.mcp.json`의 모든 서버가 자동으로 연결됩니다 (example 서버 제외)
- **서버 제어**: 연결된 서버를 개별적으로 켜고 끌 수 있습니다
- **도구 제어**: 각 서버의 도구들을 버튼으로 개별 제어 가능합니다
- **실시간 채팅**: 선택된 서버와 도구만 사용하여 Claude와 채팅할 수 있습니다

## 웹 인터페이스 사용법

1. **서버 연결 상태**: 웹 시작 시 자동으로 모든 서버 연결 시도
2. **서버 제어**: 스위치로 서버 전체를 켜고 끌 수 있음
3. **도구 제어**: 
   - 파란색 버튼: 활성화된 도구
   - 회색 버튼: 비활성화된 도구
   - 버튼 클릭으로 개별 도구 제어
   - 호버하면 도구 설명 표시
4. **채팅**: 활성화된 서버와 도구만 Claude가 사용

## 문제 해결

### 서버 연결 실패
- 서버 경로와 의존성 설치 상태 확인
- 환경 변수 설정 확인 (`.env` 파일)
- JSON 문법과 `mcpServers` 필드 포함 여부 확인
- `example`로 시작하는 서버는 자동 제외됨

### 웹 인터페이스 문제
- 브라우저에서 `http://localhost:8080` 접속 확인
- NiceGUI 의존성 설치 확인: `pip install nicegui`
- 포트 8080이 사용 중인지 확인
