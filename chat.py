from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import List
from typing import Optional
import asyncio
import nest_asyncio  # type: ignore
import json
import copy

nest_asyncio.apply()  # type: ignore

load_dotenv()

from typing import Any

def converter(obj: Any) -> Any:
    if isinstance(obj, set):
        return [str(item) for item in obj]  # type: ignore
    elif hasattr(obj, '__dict__'):
        return obj.__dict__  # Convert custom class to dict
    else:
        # Return string representation for anything else
        return str(obj)
    
class MCPChatBot:

    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.anthropic = Anthropic()
        self.available_tools: List[dict[str, Any]] = []

    async def process_query(self, messages: List[Any]) -> str:
        final_response : Optional[str] = None
        while not final_response:
            print("-------- messages --------")
            print(json.dumps(messages, indent=2, default=converter))
            print("--------------------------")
            response = await asyncio.to_thread(
                self.anthropic.messages.create,
                max_tokens=2024,
                model='claude-3-7-sonnet-20250219',
                tools=self.available_tools,  # type: ignore
                messages=messages
            )
            print("-------- response --------")
            print(json.dumps(response, indent=2, default=converter))
            print("--------------------------")
            print(">>> Processing response <<<")
            if (response.stop_reason == 'end_turn'):
                final_response = response.content[0].text  # type: ignore
                continue
            elif response.stop_reason in ['max_tokens', 'error', 'stop_sequence']:
                print(f"[{response.stop_reason}] Model stopped due to {response.stop_reason}. Response:")
                print(json.dumps(response, indent=2, default=converter))
                raise RuntimeError(f"Anthropic response stopped due to {response.stop_reason}.")
            assistant_content = []
            user_content = []
            for content in response.content:
                if content.type =='text':
                    print(f"> {content.text}")
                    assistant_content.append(content)  # type: ignore
                elif content.type == 'tool_use':
                    assistant_content.append(content)  # type: ignore
                    tool_id = content.id
                    tool_args = content.input
                    tool_name = content.name
    
                    print(f"> Calling tool {tool_name} with args {tool_args}")
                    
                    # Call a tool
                    #result = execute_tool(tool_name, tool_args): not anymore needed
                    # tool invocation through the client session
                    result = await self.session.call_tool(tool_name, arguments=tool_args)  # type: ignore
                    user_content.append({  # type: ignore
                                              "type": "tool_result",
                                              "tool_use_id":tool_id,
                                              "content": result.content
                                          }
                                        )
                else:
                    print(f"Unknown content type: {content.type}")
                    assistant_content.append(content)  # type: ignore
            messages.append({'role':'assistant', 'content':assistant_content})
            messages.append({'role':'user', 'content':user_content})
        return final_response  # type: ignore
    
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        messages = []
        while True:
            try:
                query = input("\nQuery: ").strip()
                messages.append({'role':'user', 'content':query})  # type: ignore
                if query.lower() in ['quit', 'bye', 'exit']:
                    break
                    
                response = await self.process_query(copy.deepcopy(messages))  # type: ignore
                print(f"\nResponse: {response}")
                print("\n")
                messages.append({'role':'assistant', 'content':response})  # type: ignore
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def connect_to_server_and_run(self):
        # Create server parameters for stdio connection
        server_params = StdioServerParameters(
            command="uv",  # Executable
            args=["run", "arxiv_server.py"],  # Optional command line arguments
            env=None,  # Optional environment variables
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print(f"MCP Server started with {server_params}")
                self.session = session
                # Initialize the connection
                await session.initialize()
    
                # List available tools
                response = await session.list_tools()
                
                tools = response.tools
                print("\nConnected to server with tools:", [tool.name for tool in tools])
                for tool in tools:
                    print(f"{tool.name}: {tool.description}")
                
                self.available_tools = [{
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                } for tool in response.tools]
    
                await self.chat_loop()


async def main():
    chatbot = MCPChatBot()
    await chatbot.connect_to_server_and_run()
  

if __name__ == "__main__":
    asyncio.run(main())