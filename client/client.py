import asyncio
import os
import json
from typing import Optional, Dict, List, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv
from nicegui import ui, app, run

load_dotenv()

class MCPWebClient:
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.servers: Dict[str, dict] = {}
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.connected_servers = []
        self.server_tools: Dict[str, List[dict]] = {}
        self.enabled_servers: Dict[str, bool] = {}
        self.enabled_tools: Dict[str, bool] = {}
        
    def load_mcp_config(self, config_path: str) -> Dict[str, Any]:
        """Load MCP configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'mcpServers' not in config:
                raise ValueError("Invalid MCP configuration format. Expected 'mcpServers' field.")
            
            return config['mcpServers']
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")

    async def connect_to_server(self, server_name: str, server_config: Dict[str, Any]):
        """Connect to an MCP server based on its configuration"""
        try:
            command = server_config['command']
            args = server_config.get('args', [])
            env = server_config.get('env', {})
            
            full_env = {**os.environ, **env}

            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=full_env
            )
            
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))

            await session.initialize()

            self.sessions[server_name] = session
            self.servers[server_name] = {
                'config': server_config,
                'stdio': stdio,
                'write': write
            }
            
            response = await session.list_tools()
            tools = response.tools
            
            # Store tools for this server
            self.server_tools[server_name] = []
            for tool in tools:
                tool_info = {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                self.server_tools[server_name].append(tool_info)
                tool_key = f"{server_name}::{tool.name}"
                self.enabled_tools[tool_key] = True  # Enable all tools by default
            
            self.enabled_servers[server_name] = True  # Enable server by default
            self.connected_servers.append(f"✓ {server_name} ({len(tools)} tools)")
            return True
            
        except Exception as e:
            self.connected_servers.append(f"✗ {server_name}: {str(e)}")
            return False

    async def auto_connect_all_servers(self):
        """Automatically connect to all servers from .mcp.json"""
        config_path = '.mcp.json'
        if not os.path.exists(config_path):
            return False, f"설정 파일을 찾을 수 없습니다: {config_path}"
        
        try:
            mcp_servers = self.load_mcp_config(config_path)
            
            # Exclude example servers
            filtered_servers = {
                name: config for name, config in mcp_servers.items()
                if not name.startswith('example')
            }
            
            if not filtered_servers:
                return False, "연결할 서버가 없습니다 (example 서버 제외됨)."
            
            connected_count = 0
            for server_name, server_config in filtered_servers.items():
                if await self.connect_to_server(server_name, server_config):
                    connected_count += 1
            
            return connected_count > 0, f"{connected_count}/{len(filtered_servers)}개 서버 연결 성공 (example 서버 제외)"
            
        except Exception as e:
            return False, f"연결 중 오류: {str(e)}"

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools from enabled servers only"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        available_tools = []
        
        # Only use enabled servers and tools
        for server_name, tools in self.server_tools.items():
            if not self.enabled_servers.get(server_name, False):
                continue
                
            for tool in tools:
                tool_key = f"{server_name}::{tool['name']}"
                if self.enabled_tools.get(tool_key, False):
                    available_tools.append(tool)

        # Create request parameters
        request_params = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1000,
            "messages": messages
        }
        
        # Only add tools if we have any available
        if available_tools:
            request_params["tools"] = available_tools

        # Handle multiple rounds of tool usage
        max_rounds = 10  # Prevent infinite loops
        round_count = 0
        all_tool_usage_messages = []  # Track all tool usage across rounds
        
        while round_count < max_rounds:
            response = self.anthropic.messages.create(**request_params)
            
            # Check if response contains tool calls
            has_tool_calls = any(content.type == 'tool_use' for content in response.content)
            
            if not has_tool_calls:
                # No more tool calls, return the final response
                final_response = []
                
                # Add tool usage summary if any tools were used
                if all_tool_usage_messages:
                    final_response.append("\n".join(all_tool_usage_messages))
                    final_response.append("")  # Empty line for spacing
                
                for content in response.content:
                    if content.type == 'text':
                        final_response.append(content.text)
                return "\n".join(final_response)
            
            # Process tool calls in this round
            assistant_content = []
            tool_results = []
            tool_usage_messages = []  # Track which tools were used
            
            for content in response.content:
                if content.type == 'text':
                    assistant_content.append({
                        "type": "text",
                        "text": content.text
                    })
                elif content.type == 'tool_use':
                    tool_name = content.name
                    tool_args = content.input
                    tool_use_id = content.id
                    
                    assistant_content.append({
                        "type": "tool_use",
                        "id": tool_use_id,
                        "name": tool_name,
                        "input": tool_args
                    })
                    
                    # Find the correct server for this tool
                    server_name = None
                    for srv_name, srv_tools in self.server_tools.items():
                        if not self.enabled_servers.get(srv_name, False):
                            continue
                        for srv_tool in srv_tools:
                            tool_key = f"{srv_name}::{srv_tool['name']}"
                            if srv_tool['name'] == tool_name and self.enabled_tools.get(tool_key, False):
                                server_name = srv_name
                                break
                        if server_name:
                            break
                    
                    # Execute the tool
                    if server_name and server_name in self.sessions:
                        try:
                            result = await self.sessions[server_name].call_tool(tool_name, tool_args)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": result.content
                            })
                            tool_usage_messages.append(f"🔧 도구 실행: {tool_name} (서버: {server_name})")
                        except Exception as e:
                            tool_results.append({
                                "type": "tool_result", 
                                "tool_use_id": tool_use_id,
                                "content": f"도구 실행 오류: {str(e)}"
                            })
                            tool_usage_messages.append(f"❌ 도구 실행 실패: {tool_name} - {str(e)}")
                    else:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id, 
                            "content": f"활성화된 도구 {tool_name}를 찾을 수 없음"
                        })
                        tool_usage_messages.append(f"❌ 도구를 찾을 수 없음: {tool_name}")
            
            # Add current round's tool usage messages to the global list
            all_tool_usage_messages.extend(tool_usage_messages)
            
            # Add assistant message and tool results to conversation
            messages.append({
                "role": "assistant",
                "content": assistant_content
            })
            
            messages.append({
                "role": "user",
                "content": tool_results
            })
            
            # Update request parameters for next round
            request_params["messages"] = messages
            round_count += 1
        
        # If we hit max rounds, return a message
        return "대화가 너무 길어져 중단되었습니다. 다시 시도해 주세요."
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

# Global client instance
client = MCPWebClient()

# Global UI components that need to be updated
server_control_section = None
chat_section = None
status_area = None
server_controls_container = None

async def update_server_controls():
    """Update server control switches and tool buttons"""
    if not server_controls_container:
        return
        
    server_controls_container.clear()
    for server_name in client.enabled_servers.keys():
        with server_controls_container:
            # Server switch
            enabled = client.enabled_servers[server_name]
            switch = ui.switch(f'{server_name} ({len(client.server_tools.get(server_name, []))} tools)', 
                             value=enabled)
            
            def make_server_toggle(name):
                async def toggle_server(value):
                    client.enabled_servers[name] = value.value
                    await update_server_controls()  # Refresh entire UI
                return toggle_server
            
            switch.on_value_change(make_server_toggle(server_name))
            
            # Tool buttons (only show when server is enabled)
            if enabled:
                with ui.column().classes('ml-8 mt-2 mb-4'):
                    tools = client.server_tools.get(server_name, [])
                    if tools:
                        # Group tools in rows of 4
                        for i in range(0, len(tools), 4):
                            with ui.row().classes('gap-2'):
                                for tool in tools[i:i+4]:
                                    tool_key = f"{server_name}::{tool['name']}"
                                    tool_enabled = client.enabled_tools.get(tool_key, True)
                                    
                                    def make_tool_button(key, tool_name, description):
                                        def toggle_tool():
                                            current_state = client.enabled_tools.get(key, True)
                                            client.enabled_tools[key] = not current_state
                                            # Update UI immediately
                                            asyncio.create_task(update_server_controls())
                                        return toggle_tool
                                    
                                    # Tool button with color based on enabled state
                                    color = 'primary' if tool_enabled else 'grey'
                                    btn = ui.button(
                                        tool['name'], 
                                        color=color,
                                        on_click=make_tool_button(tool_key, tool['name'], tool['description'])
                                    ).props('size=sm').tooltip(tool['description'])

async def update_tool_controls():
    """Deprecated - tool controls are now integrated with server controls"""
    pass

async def initialize_app():
    """Initialize the application by connecting to all servers"""
    global status_area, server_control_section, chat_section
    
    try:
        if status_area:
            status_area.value = "자동 서버 연결 중..."
        
        success, message = await client.auto_connect_all_servers()
        
        if status_area:
            status_area.value = message + "\n\n연결된 서버:\n" + "\n".join(client.connected_servers)
        
        if success:
            if server_control_section:
                server_control_section.visible = True
            if chat_section:
                chat_section.visible = True
            await update_server_controls()
    except Exception as e:
        if status_area:
            status_area.value = f"자동 연결 중 오류: {str(e)}"

@ui.page('/')
def main_page():
    global status_area, server_control_section, chat_section
    global server_controls_container
    
    ui.page_title('MCP Web Client')
    
    with ui.header():
        ui.label('MCP Web Client').classes('text-h4')
    
    with ui.column().classes('w-full max-w-6xl mx-auto p-4'):
        # Connection status section
        with ui.card().classes('w-full mb-4'):
            ui.label('서버 연결 상태').classes('text-h6 mb-2')
            status_area = ui.textarea('초기화 중...').classes('w-full')
            status_area.props('readonly')
        
        # Server and tool control section (initially hidden)
        with ui.card().classes('w-full mb-4') as server_control_section:
            server_control_section.visible = False
            ui.label('서버 및 도구 제어').classes('text-h6 mb-2')
            ui.label('서버를 끄면 해당 서버의 모든 도구가 비활성화됩니다. 개별 도구는 버튼을 클릭해서 켜고 끌 수 있습니다.').classes('text-sm text-gray-600 mb-4')
            server_controls_container = ui.column()
            
        # Auto-initialize when page loads
        ui.timer(0.1, initialize_app, once=True)
        
        # Chat section (initially hidden)
        with ui.card().classes('w-full') as chat_section:
            chat_section.visible = False
            ui.label('채팅').classes('text-h6 mb-2')
            
            chat_history = ui.html().classes('w-full border p-4 mb-4 bg-gray-50 min-h-64 max-h-96 overflow-y-auto')
            
            with ui.row().classes('w-full'):
                query_input = ui.input('질문을 입력하세요...').classes('flex-grow')
                send_btn = ui.button('전송', color='primary')
            
            async def send_query():
                if not query_input.value.strip():
                    return
                
                query = query_input.value
                query_input.value = ''
                
                # Add user message to chat
                chat_history.content += f'<div class="mb-2"><strong>사용자:</strong> {query}</div>'
                
                try:
                    # Add loading indicator
                    chat_history.content += '<div class="mb-2"><strong>AI:</strong> <em>응답 생성 중...</em></div>'
                    
                    response = await client.process_query(query)
                    
                    # Replace loading indicator with actual response
                    chat_content = chat_history.content
                    last_loading_idx = chat_content.rfind('<div class="mb-2"><strong>AI:</strong> <em>응답 생성 중...</em></div>')
                    if last_loading_idx != -1:
                        chat_history.content = (
                            chat_content[:last_loading_idx] + 
                            f'<div class="mb-2"><strong>AI:</strong> <pre style="white-space: pre-wrap; word-wrap: break-word;">{response}</pre></div>'
                        )
                    
                except Exception as e:
                    # Replace loading indicator with error message
                    chat_content = chat_history.content
                    last_loading_idx = chat_content.rfind('<div class="mb-2"><strong>AI:</strong> <em>응답 생성 중...</em></div>')
                    if last_loading_idx != -1:
                        chat_history.content = (
                            chat_content[:last_loading_idx] + 
                            f'<div class="mb-2"><strong>오류:</strong> {str(e)}</div>'
                        )
            
            send_btn.on_click(send_query)
            query_input.on('keydown.enter', send_query)

# Handle app shutdown
async def cleanup():
    await client.cleanup()

app.on_shutdown(cleanup)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='MCP Web Client', port=8080, host='0.0.0.0')