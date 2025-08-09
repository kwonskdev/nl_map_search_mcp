# MCP Client

MCP (Model Context Protocol) 표준 클라이언트로, MCP 서버에 연결하여 Claude와 함께 도구를 사용할 수 있습니다.

## 설치

```bash
cd client
uv sync
```

## 설정 파일

`.mcp.json` 파일을 생성하여 연결할 서버들을 설정합니다:

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

> **참고**: `example`로 시작하는 서버들은 자동으로 제외됩니다. 특정 example 서버를 사용하려면 `--servers` 옵션으로 명시적으로 지정하세요.

## 환경 변수

`.env` 파일에 필요한 환경 변수를 설정하세요:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
```

## 사용법

```bash
# 기본 사용 (example 서버 제외하고 자동 연결)
uv run client.py

# 특정 설정 파일 사용
uv run client.py --config my-config.mcp.json

# 특정 서버만 연결 (example 서버도 포함 가능)
uv run client.py --servers naver-openapi example-test-server
```

## 문제 해결

### 서버 연결 실패
- 서버 경로와 의존성 설치 상태 확인
- 환경 변수 설정 확인
- JSON 문법과 `mcpServers` 필드 포함 여부 확인
