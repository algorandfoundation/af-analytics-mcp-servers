import asyncio
import sys
from typing import Optional, List, Dict
from contextlib import AsyncExitStack
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self, system_prompt: Optional[str] = None):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.conversation_history: List[Dict] = []

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": query
        })

        response = await self.session.list_tools()
        available_tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call with system prompt and conversation history
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=self.system_prompt,  # Add system prompt here
            messages=self.conversation_history,
            tools=available_tools
        )

        # Process response and handle tool calls
        assistant_response_parts = []
        
        while response.stop_reason == "tool_use":
            # Collect all content from this turn
            assistant_content = []
            
            for content in response.content:
                if content.type == 'text':
                    assistant_response_parts.append(content.text)
                    assistant_content.append(content.model_dump())
                elif content.type == 'tool_use':
                    tool_name = content.name
                    tool_args = content.input
                    
                    print(f"\n🔧 Calling tool: {tool_name}")
                    
                    # Add to assistant content
                    assistant_content.append(content.model_dump())
                    
                    # Execute tool call
                    result = await self.session.call_tool(tool_name, tool_args)
                    
                    # Add assistant message with tool use
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": assistant_content
                    })
                    
                    # Add tool result as user message
                    self.conversation_history.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }]
                    })
                    
                    # Reset for next iteration
                    assistant_content = []

            # Get next response from Claude with updated conversation
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=self.system_prompt,
                messages=self.conversation_history,
                tools=available_tools
            )

        # Handle final response (non-tool-use)
        final_text = []
        final_content = []
        
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                final_content.append(content.model_dump())

        # Add final assistant response to history
        if final_content:
            self.conversation_history.append({
                "role": "assistant",
                "content": final_content
            })

        return "\n".join(final_text) if final_text else "No response generated."

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("✓ Conversation history cleared.")

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\n" + "="*60)
        print("  Paul - Algorand Analytics Assistant")
        print("="*60)
        print("\nCommands:")
        print("  • Type your message to chat with Paul")
        print("  • 'quit' or 'exit' - End the conversation")
        print("  • 'clear' - Clear conversation history")
        print("  • 'prompt' - View system prompt")
        print("="*60 + "\n")
        
        while True:
            try:
                query = input("\n🔵 You: ").strip()
                
                if query.lower() in ['quit', 'exit']:
                    print("\n👋 Ending conversation. Goodbye!")
                    break
                
                if query.lower() == 'clear':
                    self.clear_history()
                    continue
                
                if query.lower() == 'prompt':
                    print("\n" + "="*60)
                    print("CURRENT SYSTEM PROMPT:")
                    print("="*60)
                    print(self.system_prompt)
                    print("="*60)
                    continue
                
                if not query:
                    continue
                    
                print("\n🟢 Paul: ", end="", flush=True)
                response = await self.process_query(query)
                print(response)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Conversation interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

def load_system_prompt(prompt_path: str = "docs/prompt.txt") -> str:
    """Load system prompt from file"""
    try:
        prompt_file = Path(prompt_path)
        system_prompt = prompt_file.read_text(encoding="utf-8")
        print(f"✓ Loaded system prompt from {prompt_path}")
        return system_prompt
    except FileNotFoundError:
        print(f"⚠ Warning: {prompt_path} not found, using default prompt")
        return "You are Paul, a helpful AI assistant specialized in Algorand blockchain analytics."

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script> [path_to_prompt]")
        print("\nExample:")
        print("  python client.py server.py")
        print("  python client.py server.py docs/prompt.txt")
        sys.exit(1)
    
    # Load system prompt
    prompt_path = sys.argv[2] if len(sys.argv) > 2 else "docs/prompt.txt"
    system_prompt = load_system_prompt(prompt_path)
    
    # Create client with system prompt
    client = MCPClient(system_prompt=system_prompt)
    
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())