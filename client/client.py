import asyncio
import os
from typing import Optional, Dict, List
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.sessions: Dict[str, ClientSession] = {}
        self.servers: Dict[str, dict] = {}
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self, server_script_path: str, server_name: str = None):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
            server_name: Optional name for the server (defaults to filename without extension)
        """
        directory = os.path.dirname(server_script_path)
        script_name = os.path.basename(server_script_path)
        server_name = server_name or os.path.splitext(script_name)[0]
            
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        command = "uv" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=["--directory", directory, "run", script_name],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        
        await session.initialize()
        
        # Store server info
        self.sessions[server_name] = session
        self.servers[server_name] = {
            'path': server_script_path,
            'stdio': stdio,
            'write': write
        }
        
        # List available tools
        response = await session.list_tools()
        tools = response.tools
        print(f"\nConnected to server '{server_name}' with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools from all connected servers"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # Collect tools from all connected servers
        available_tools = []
        tool_to_server = {}
        
        for server_name, session in self.sessions.items():
            response = await session.list_tools()
            for tool in response.tools:
                tool_info = {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                }
                available_tools.append(tool_info)
                tool_to_server[tool.name] = server_name

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                # Execute tool call on the appropriate server
                server_name = tool_to_server.get(tool_name)
                if server_name and server_name in self.sessions:
                    result = await self.sessions[server_name].call_tool(tool_name, tool_args)
                    final_text.append(f"[Calling tool {tool_name} on server '{server_name}' with args {tool_args}]")
                else:
                    final_text.append(f"[Error: Tool {tool_name} not found on any connected server]")
                    continue

                # Continue conversation with tool results
                if hasattr(content, 'text') and content.text:
                    messages.append({
                      "role": "assistant",
                      "content": content.text
                    })
                messages.append({
                    "role": "user", 
                    "content": result.content
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await self.process_query(query)
                print("\n" + response)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script1> [path_to_server_script2] [...]")
        sys.exit(1)
        
    client = MCPClient()
    try:
        # Connect to all provided servers
        for server_path in sys.argv[1:]:
            await client.connect_to_server(server_path, "Naver OpenAPI")
            
        print(f"\nConnected to {len(sys.argv[1:])} server(s)")
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())