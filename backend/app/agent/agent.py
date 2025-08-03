import anthropic
import os
import json
from tools.example import weather, news
from utils import print_thinking_response, count_tokens

# Global variables for model and token budgets
MODEL_NAME = "claude-3-7-sonnet-20250219"
MAX_TOKENS = 4000
THINKING_BUDGET_TOKENS = 2000

# Set your API key as an environment variable or directly
# os.environ["ANTHROPIC_API_KEY"] = "your_api_key_here"

# Initialize the client
client = anthropic.Anthropic()

# We can just call this function from a chat or workflow service
def multiple_tool_calls_with_thinking():
    # Define tools
    tools = [
        {
            "name": "weather",
            "description": "Get current weather information for a location.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get weather for."
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "news",
            "description": "Get latest news headlines for a topic.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to get news about."
                    }
                },
                "required": ["topic"]
            }
        }
    ]
    
    # Initial request
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=MAX_TOKENS,
        thinking={
                "type": "enabled",
                "budget_tokens": THINKING_BUDGET_TOKENS
        },
        tools=tools,
        messages=[{
            "role": "user",
            "content": "What's the weather in London, and can you also tell me the latest news about technology?"
        }]
    )
    
    # Print detailed information about initial response
    print("\n=== INITIAL RESPONSE ===")
    print(f"Response ID: {response.id}")
    print(f"Stop reason: {response.stop_reason}")
    print(f"Model: {response.model}")
    print(f"Content blocks: {len(response.content)} blocks")
    
    # Print each content block
    for i, block in enumerate(response.content):
        print(f"\nBlock {i+1}: Type = {block.type}")
        if block.type == "thinking":
            print(f"Thinking content: {block.thinking[:150]}...")
            print(f"Signature available: {bool(getattr(block, 'signature', None))}")
        elif block.type == "text":
            print(f"Text content: {block.text}")
        elif block.type == "tool_use":
            print(f"Tool: {block.name}")
            print(f"Tool input: {block.input}")
            print(f"Tool ID: {block.id}")
    print("=== END INITIAL RESPONSE ===\n")
    
    # Handle potentially multiple tool calls
    full_conversation = [{
        "role": "user",
        "content": "What's the weather in London, and can you also tell me the latest news about technology?"
    }]
    
    # Track iteration count for multi-turn tool use
    iteration = 0
    
    while response.stop_reason == "tool_use":
        iteration += 1
        print(f"\n=== TOOL USE ITERATION {iteration} ===")
        
        # Extract thinking blocks and tool use to include in conversation history
        assistant_blocks = []
        for block in response.content:
            if block.type in ["thinking", "redacted_thinking", "tool_use"]:
                assistant_blocks.append(block)
        
        # Add assistant response with thinking blocks and tool use
        full_conversation.append({
            "role": "assistant",
            "content": assistant_blocks
        })
        
        # Find the tool_use block
        tool_use_block = next((block for block in response.content if block.type == "tool_use"), None)
        if tool_use_block:
            print(f"\n=== EXECUTING TOOL ===")
            print(f"Tool name: {tool_use_block.name}")
            
            # Execute the appropriate tool
            if tool_use_block.name == "weather":
                print(f"Location to check: {tool_use_block.input['location']}")
                tool_result = weather(tool_use_block.input["location"])
            elif tool_use_block.name == "news":
                print(f"Topic to check: {tool_use_block.input['topic']}")
                tool_result = news(tool_use_block.input["topic"])
            else:
                tool_result = {"error": "Unknown tool"}
                
            print(f"Result: {tool_result}")
            print("=== TOOL EXECUTION COMPLETE ===\n")
            
            # Add tool result to conversation
            full_conversation.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": json.dumps(tool_result)
                }]
            })
            
            # Continue the conversation
            print("\n=== SENDING FOLLOW-UP REQUEST WITH TOOL RESULT ===")
            response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                thinking={
                        "type": "enabled",
                        "budget_tokens": THINKING_BUDGET_TOKENS
                },
                tools=tools,
                messages=full_conversation
            )
            
            # Print follow-up response details
            print(f"\n=== FOLLOW-UP RESPONSE (ITERATION {iteration}) ===")
            print(f"Response ID: {response.id}")
            print(f"Stop reason: {response.stop_reason}")
            print(f"Content blocks: {len(response.content)} blocks")
            
            for i, block in enumerate(response.content):
                print(f"\nBlock {i+1}: Type = {block.type}")
                if block.type == "thinking":
                    print(f"Thinking content preview: {block.thinking[:100]}...")
                elif block.type == "text":
                    print(f"Text content preview: {block.text[:100]}...")
                elif block.type == "tool_use":
                    print(f"Tool: {block.name}")
                    print(f"Tool input preview: {str(block.input)[:100]}")
            print(f"=== END FOLLOW-UP RESPONSE (ITERATION {iteration}) ===\n")
            
            if response.stop_reason != "tool_use":
                print("\n=== FINAL RESPONSE ===")
                print_thinking_response(response)
                print("=== END FINAL RESPONSE ===")
        else:
            print("No tool_use block found in response.")
            break

