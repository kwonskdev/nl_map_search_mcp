import asyncio
import os
import json
from typing import Optional, Dict, List, Any
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

    def load_mcp_config(self, config_path: str) -> Dict[str, Any]:
        """Load MCP configuration from JSON file
        
        Args:
            config_path: Path to the MCP configuration file (.mcp.json)
            
        Returns:
            Dictionary containing MCP server configurations
        """
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
        """Connect to an MCP server based on its configuration
        
        Args:
            server_name: Name of the server
            server_config: MCP server configuration dictionary
        """
        print(f"Connecting to server '{server_name}'...")
        
        try:
            command = server_config['command']
            args = server_config.get('args', [])
            env = server_config.get('env', {})
            
            # Merge with current environment
            full_env = {**os.environ, **env}

            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=full_env
            )
            # breakpoint()
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
            
            # List available tools
            response = await session.list_tools()
            tools = response.tools
            print(f"✓ Connected to server '{server_name}' with {len(tools)} tools: {[tool.name for tool in tools]}")
            
        except Exception as e:
            print(f"✗ Failed to connect to server '{server_name}': {str(e)}")
            raise

    async def connect_from_config_file(self, config_path: str, server_names: Optional[List[str]] = None):
        """Connect to servers specified in an MCP configuration file
        
        Args:
            config_path: Path to the MCP configuration file (.mcp.json)
            server_names: Optional list of specific server names to connect to.
                         If None, connects to all servers in the config (excluding examples).
        """
        mcp_servers = self.load_mcp_config(config_path)
        
        if server_names:
            # Filter servers by name
            filtered_servers = {
                name: config for name, config in mcp_servers.items() 
                if name in server_names
            }
            if not filtered_servers:
                raise ValueError(f"No servers found with names: {server_names}")
            mcp_servers = filtered_servers
        else:
            # Exclude example servers when no specific servers are requested
            mcp_servers = {
                name: config for name, config in mcp_servers.items()
                if not name.startswith('example')
            }
        
        if not mcp_servers:
            print("No servers to connect to (all servers are examples or excluded)")
            return
        
        print(f"Loading {len(mcp_servers)} server(s) from MCP configuration...")
        
        connected_servers = []
        for server_name, server_config in mcp_servers.items():
            try:
                await self.connect_to_server(server_name, server_config)
                connected_servers.append(server_name)
            except Exception as e:
                print(f"Warning: Skipping server '{server_name}' due to error: {e}")
                continue
        
        if connected_servers:
            print(f"✓ Successfully connected to {len(connected_servers)} server(s): {', '.join(connected_servers)}")
        else:
            print("✗ Failed to connect to any servers")

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
    """Main function"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP Client - Model Context Protocol Client')
    parser.add_argument('--config', '-c', 
                       help='Path to MCP configuration file (.mcp.json)')
    parser.add_argument('--servers', '-s', nargs='*',
                       help='Specific server names to connect to (from config)')
    
    args = parser.parse_args()
    
    client = MCPClient()
    try:
        if args.config:
            # Use specified MCP configuration file
            await client.connect_from_config_file(args.config, args.servers)
        else:
            # Default: look for .mcp.json in the same directory
            default_config = os.path.join(os.path.dirname(__file__), '.mcp.json')
            if os.path.exists(default_config):
                print(f"Using default configuration: {default_config}")
                await client.connect_from_config_file(default_config, args.servers)
            else:
                print("Error: No MCP configuration file found.")
                print("Usage:")
                print("  python client.py --config path/to/.mcp.json")
                print("  python client.py --config .mcp.json --servers server1 server2")
                print(f"\nExpected default configuration file: {default_config}")
                sys.exit(1)
            
        if client.sessions:
            await client.chat_loop()
        else:
            print("No servers connected. Exiting.")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())