import anthropic  # type: ignore
import json
import re
from app.agent.tools.functions import (  # type: ignore
    analyze_results,
    analyze_user_account,
    parse_composio_search_results,
    parse_composio_finance_search_results,
    parse_composio_news_search_results,
    parse_composio_event_search_results,
)
from app.agent.tools.definitions import tool_definitions  # type: ignore
from composio import Composio  # type: ignore
from app.chat.accounts.data import mock_user_data  # type: ignore


class CalenderService:
    def __init__(self):
        # Initialize the Anthropic client
        self.client = anthropic.Anthropic()
        self.model_name = "claude-sonnet-4-20250514"
        self.max_tokens = 4000
        self.thinking_budget_tokens = 2000

        # Initialize Composio
        self.composio = Composio()
        self.user_id = "0000-1111-2222"

        # Define tools (same as agent.py)
        self.tools = tool_definitions

        # System prompt for financial planning agent
        self.system_prompt = """You are Rocket, an expert Financial Planning Assistant with access to powerful analytical tools and real-time financial data. Your mission is to provide comprehensive, personalized financial guidance by leveraging user account analysis, market research, and current financial news.

## Core Capabilities

**Financial Analysis Tools:**
- `analyze_user_account`: Deep analysis of user's spending patterns, income, account balances, and financial health
- `COMPOSIO_SEARCH_FINANCE_SEARCH`: Real-time stock prices, market data, financial metrics, and investment information
- `COMPOSIO_SEARCH_NEWS_SEARCH`: Current financial news, market trends, economic updates, and investment insights
- `COMPOSIO_SEARCH_EVENT_SEARCH`: Financial events, earnings announcements, market calendars
- `analyze_results`: Process and synthesize tool outputs for actionable insights

## Operating Methodology

**1. Initial Assessment**
- Always start by analyzing the user's current financial situation using `analyze_user_account`
- Identify spending patterns, income sources, savings rates, and financial goals
- Look for immediate optimization opportunities and potential risks

**2. Market Context Research**
- Use financial search tools to gather relevant market information based on user's situation
- Research investment opportunities, market trends, or specific financial products mentioned
- Stay current with financial news that could impact user's financial planning

**3. Comprehensive Analysis**
- Synthesize user data with market information using `analyze_results`
- Consider both short-term financial health and long-term planning strategies
- Factor in current economic conditions and market sentiment

**4. Actionable Recommendations**
- Provide specific, prioritized action items
- Include concrete steps, timelines, and expected outcomes
- Tailor advice to user's risk tolerance and financial goals

## Key Financial Planning Areas

**Budgeting & Cash Flow:**
- Analyze spending patterns across categories (housing, food, transportation, entertainment)
- Identify areas for cost optimization without sacrificing quality of life
- Recommend emergency fund targets and savings strategies

**Investment Strategy:**
- Research current market conditions and investment opportunities
- Suggest asset allocation based on age, risk tolerance, and goals
- Provide insights on specific stocks, funds, or investment vehicles

**Debt Management:**
- Analyze existing debts and payment strategies
- Research current interest rates and refinancing opportunities
- Prioritize debt payoff strategies (avalanche vs. snowball)

**Tax Optimization:**
- Identify tax-advantaged accounts and strategies
- Research current tax law changes affecting financial planning
- Suggest timing for financial moves to optimize tax outcomes

**Risk Management:**
- Evaluate insurance needs and coverage gaps
- Research insurance products and providers
- Plan for financial contingencies and unexpected events

## Tool Usage Patterns

**Multi-Tool Analysis Sequences:**
1. `analyze_user_account` → `COMPOSIO_SEARCH_FINANCE_SEARCH` → `analyze_results`
2. User question → `COMPOSIO_SEARCH_NEWS_SEARCH` → `COMPOSIO_SEARCH_FINANCE_SEARCH` → recommendations
3. `analyze_user_account` → `COMPOSIO_SEARCH_EVENT_SEARCH` → strategic planning

**When to Use Each Tool:**
- Start with `analyze_user_account` for any financial planning discussion
- Use finance search for market data, stock prices, investment research
- Use news search for current events affecting financial decisions
- Use event search for timing financial moves around market events
- Use `analyze_results` to synthesize complex multi-tool outputs

## Communication Style

**Be Comprehensive Yet Accessible:**
- Explain financial concepts in clear, non-technical language
- Provide context for recommendations with supporting data
- Use specific numbers and percentages from analysis tools

**Structure Your Responses:**
- Lead with key insights from account analysis
- Present market context and relevant research
- Conclude with prioritized, actionable recommendations
- Include specific next steps and timelines
- Conversational, maximum 400 characters, IMPORTANT!!!

**Maintain Professionalism:**
- Act as a trusted financial advisor, not just an information provider
- Consider the user's emotional relationship with money
- Provide encouragement while being realistic about challenges

## Example Response Flow

User: "How should I adjust my spending?"

1. 🔍 **Analyze Current Situation**: Use `analyze_user_account` to understand spending patterns
2. 📊 **Research Market Context**: Use financial search for current economic conditions affecting budgeting
3. 📰 **Check Recent News**: Search for relevant financial news about inflation, interest rates, or economic trends
4. 🎯 **Synthesize Insights**: Use `analyze_results` to combine user data with market information
5. 💡 **Provide Recommendations**: Deliver specific, actionable spending adjustments with rationale

Remember: Always ground your advice in the user's actual financial data combined with current market realities. Use multiple tools when needed to provide the most comprehensive and current financial guidance possible."""

    def process_message(self, user_message):
        """
        Process a user message using the agent's multiple_tool_calls_with_thinking logic.
        Returns structured response data for the frontend.
        """
        print("\n=== CHAT SERVICE: Processing new message ===")
        print(f"User message: {user_message}")
        print(f"Model: {self.model_name}")
        print(f"Max tokens: {self.max_tokens}")

        try:
            # Initial request (same structure as agent.py)
            print("\n--- Making initial API call to Claude ---")
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                thinking={
                    "type": "enabled",
                    "budget_tokens": self.thinking_budget_tokens,
                },
                tools=self.tools,
                system=self.system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            print(f"Initial response stop_reason: {response.stop_reason}")
            print(f"Initial response content blocks: {len(response.content)}")

            # Process the response and handle tool calls
            conversation_history = [{"role": "user", "content": user_message}]
            print(
                f"Starting conversation history with {len(conversation_history)} messages"
            )

            final_response = self._handle_response_chain(response, conversation_history)

            print("\n=== CHAT SERVICE: Processing complete ===")
            print(f"Final response blocks: {len(final_response.get('blocks', []))}")
            print(f"Total iterations: {final_response.get('total_iterations', 0)}")
            print(f"Stop reason: {final_response.get('stop_reason', 'unknown')}")

            return {"success": True, "response": final_response}

        except Exception as e:
            print("\n!!! CHAT SERVICE ERROR !!!")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            import traceback

            print(f"Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    def process_message_stream(self, user_message):
        """
        Process a user message using the agent's multiple_tool_calls_with_thinking logic.
        Yields structured response data blocks for SSE streaming.
        """
        print("\n=== CHAT SERVICE: Processing new message (STREAMING) ===")
        print(f"User message: {user_message}")
        print(f"Model: {self.model_name}")
        print(f"Max tokens: {self.max_tokens}")

        try:
            # Initial request (same structure as agent.py)
            print("\n--- Making initial API call to Claude ---")
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                thinking={
                    "type": "enabled",
                    "budget_tokens": self.thinking_budget_tokens,
                },
                tools=self.tools,
                system=self.system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            print(f"Initial response stop_reason: {response.stop_reason}")
            print(f"Initial response content blocks: {len(response.content)}")

            # Process the response and handle tool calls
            conversation_history = [{"role": "user", "content": user_message}]
            print(
                f"Starting conversation history with {len(conversation_history)} messages"
            )

            # Stream the response chain
            yield from self._handle_response_chain_stream(
                response, conversation_history
            )

            print("\n=== CHAT SERVICE: Processing complete (STREAMING) ===")

        except Exception as e:
            print("\n!!! CHAT SERVICE ERROR (STREAMING) !!!")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            import traceback

            print(f"Traceback: {traceback.format_exc()}")

            yield {"type": "error", "error": str(e)}

    def _handle_response_chain_stream(self, response, conversation_history):
        """
        Handle the full response chain including tool calls, streaming blocks as they're processed.
        Yields structured response data blocks for SSE.
        """
        print("\n--- Starting response chain handling (STREAMING) ---")
        iteration = 0
        total_blocks_sent = 0

        while response.stop_reason == "tool_use":
            iteration += 1
            print(f"\n*** ITERATION {iteration} (STREAMING) ***")
            print(f"Stop reason: {response.stop_reason}")
            print(f"Content blocks in response: {len(response.content)}")

            # Log block types in this response
            block_types = [block.type for block in response.content]
            print(f"Block types: {block_types}")

            # Extract and stream blocks from current response
            for block in response.content:
                block_data = None
                if block.type == "thinking":
                    block_data = {
                        "type": "thinking",
                        "content": block.thinking,
                        "iteration": iteration,
                    }
                elif block.type == "redacted_thinking":
                    block_data = {
                        "type": "redacted_thinking",
                        "content": "[Thinking content redacted]",
                        "iteration": iteration,
                    }
                elif block.type == "text":
                    block_data = {
                        "type": "text",
                        "content": block.text,
                        "iteration": iteration,
                    }
                elif block.type == "tool_use":
                    block_data = {
                        "type": "tool_use",
                        "tool_name": block.name,
                        "tool_input": block.input,
                        "tool_id": block.id,
                        "iteration": iteration,
                    }

                if block_data:
                    yield {"type": "block", "block": block_data}
                    total_blocks_sent += 1
                    print(f"Streamed block {total_blocks_sent}: {block_data['type']}")

            # Add assistant response to conversation history
            assistant_blocks = []
            for block in response.content:
                if block.type in ["thinking", "redacted_thinking", "tool_use"]:
                    assistant_blocks.append(block)

            conversation_history.append(
                {"role": "assistant", "content": assistant_blocks}
            )
            print("Added assistant message to conversation history")

            # Execute ALL tool_use blocks if there are any
            tool_use_blocks = [
                block for block in response.content if block.type == "tool_use"
            ]
            if tool_use_blocks:
                print(
                    f"*** TOOL EXECUTION ({len(tool_use_blocks)} tools) (STREAMING) ***"
                )

                # Collect all tool results
                tool_results_content = []

                for tool_use_block in tool_use_blocks:
                    print(f"Tool name: {tool_use_block.name}")
                    print(f"Tool input: {tool_use_block.input}")
                    print(f"Tool ID: {tool_use_block.id}")

                    # Execute the tool
                    tool_result = self._execute_tool(
                        tool_use_block.name, tool_use_block.input
                    )
                    print(f"Tool execution result: {tool_result}")

                    # Stream tool result block
                    tool_result_data = {
                        "type": "tool_result",
                        "tool_name": tool_use_block.name,
                        "tool_input": tool_use_block.input,
                        "tool_result": tool_result,
                        "iteration": iteration,
                    }

                    yield {"type": "block", "block": tool_result_data}
                    total_blocks_sent += 1
                    print(f"Streamed tool result block {total_blocks_sent}")

                    # Collect tool result for conversation history
                    tool_results_content.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_block.id,
                            "content": json.dumps(tool_result),
                        }
                    )

                # Add ALL tool results to conversation in a single message
                conversation_history.append(
                    {
                        "role": "user",
                        "content": tool_results_content,
                    }
                )
                print(
                    f"Added {len(tool_results_content)} tool results to conversation history. Total messages: {len(conversation_history)}"
                )

                # Continue the conversation
                print("*** CONTINUING CONVERSATION AFTER TOOL USE (STREAMING) ***")
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=self.max_tokens,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": self.thinking_budget_tokens,
                    },
                    tools=self.tools,
                    system=self.system_prompt,
                    messages=conversation_history,
                )
            else:
                print("No tool_use block found, breaking loop")
                break

        # Handle final response (no more tool use)
        print("\n*** FINAL RESPONSE PROCESSING (STREAMING) ***")
        print(f"Final stop reason: {response.stop_reason}")
        if response.stop_reason != "tool_use":
            for block in response.content:
                block_data = None
                if block.type == "thinking":
                    block_data = {
                        "type": "thinking",
                        "content": block.thinking,
                        "iteration": iteration + 1,
                    }
                elif block.type == "redacted_thinking":
                    block_data = {
                        "type": "redacted_thinking",
                        "content": "[Thinking content redacted]",
                        "iteration": iteration + 1,
                    }
                elif block.type == "text":
                    block_data = {
                        "type": "text",
                        "content": block.text,
                        "iteration": iteration + 1,
                    }

                if block_data:
                    yield {"type": "block", "block": block_data}
                    total_blocks_sent += 1
                    print(
                        f"Streamed final block {total_blocks_sent}: {block_data['type']}"
                    )

        # Send completion event
        print("\n--- Response chain handling complete (STREAMING) ---")
        print(f"Total blocks streamed: {total_blocks_sent}")
        print(f"Total iterations: {iteration + 1}")

        yield {
            "type": "complete",
            "stop_reason": response.stop_reason,
            "total_iterations": iteration + 1,
            "total_blocks": total_blocks_sent,
        }

    def _handle_response_chain(self, response, conversation_history):
        """
        Handle the full response chain including tool calls, following agent.py logic.
        Returns structured response data.
        """
        print("\n--- Starting response chain handling ---")
        response_blocks = []
        iteration = 0

        while response.stop_reason == "tool_use":
            iteration += 1
            print(f"\n*** ITERATION {iteration} ***")
            print(f"Stop reason: {response.stop_reason}")
            print(f"Content blocks in response: {len(response.content)}")

            # Log block types in this response
            block_types = [block.type for block in response.content]
            print(f"Block types: {block_types}")

            # Extract blocks from current response
            current_blocks = []
            for block in response.content:
                if block.type == "thinking":
                    current_blocks.append(
                        {
                            "type": "thinking",
                            "content": block.thinking,
                            "iteration": iteration,
                        }
                    )
                elif block.type == "redacted_thinking":
                    current_blocks.append(
                        {
                            "type": "redacted_thinking",
                            "content": "[Thinking content redacted]",
                            "iteration": iteration,
                        }
                    )
                elif block.type == "text":
                    current_blocks.append(
                        {"type": "text", "content": block.text, "iteration": iteration}
                    )
                elif block.type == "tool_use":
                    current_blocks.append(
                        {
                            "type": "tool_use",
                            "tool_name": block.name,
                            "tool_input": block.input,
                            "tool_id": block.id,
                            "iteration": iteration,
                        }
                    )

            response_blocks.extend(current_blocks)
            print(f"Added {len(current_blocks)} blocks to response")

            # Add assistant response to conversation history
            assistant_blocks = []
            for block in response.content:
                if block.type in ["thinking", "redacted_thinking", "tool_use"]:
                    assistant_blocks.append(block)

            conversation_history.append(
                {"role": "assistant", "content": assistant_blocks}
            )
            print("Added assistant message to conversation history")

            # Execute ALL tool_use blocks if there are any
            tool_use_blocks = [
                block for block in response.content if block.type == "tool_use"
            ]
            if tool_use_blocks:
                print(f"*** TOOL EXECUTION ({len(tool_use_blocks)} tools) ***")

                # Collect all tool results
                tool_results_content = []

                for tool_use_block in tool_use_blocks:
                    print(f"Tool name: {tool_use_block.name}")
                    print(f"Tool input: {tool_use_block.input}")
                    print(f"Tool ID: {tool_use_block.id}")

                    # Execute the tool
                    tool_result = self._execute_tool(
                        tool_use_block.name, tool_use_block.input
                    )
                    print(f"Tool execution result: {tool_result}")

                    # Add tool result to response blocks
                    response_blocks.append(
                        {
                            "type": "tool_result",
                            "tool_name": tool_use_block.name,
                            "tool_input": tool_use_block.input,
                            "tool_result": tool_result,
                            "iteration": iteration,
                        }
                    )

                    # Collect tool result for conversation history
                    tool_results_content.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_block.id,
                            "content": json.dumps(tool_result),
                        }
                    )

                print("Added all tool results to response blocks")

                # Add ALL tool results to conversation in a single message
                conversation_history.append(
                    {
                        "role": "user",
                        "content": tool_results_content,
                    }
                )
                print(
                    f"Added {len(tool_results_content)} tool results to conversation history. Total messages: {len(conversation_history)}"
                )

                # Continue the conversation
                print("*** CONTINUING CONVERSATION AFTER TOOL USE ***")
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=self.max_tokens,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": self.thinking_budget_tokens,
                    },
                    tools=self.tools,
                    system=self.system_prompt,
                    messages=conversation_history,
                )
            else:
                print("No tool_use block found, breaking loop")
                break

        # Handle final response (no more tool use)
        print("\n*** FINAL RESPONSE PROCESSING ***")
        print(f"Final stop reason: {response.stop_reason}")
        if response.stop_reason != "tool_use":
            final_blocks = []
            for block in response.content:
                if block.type == "thinking":
                    final_blocks.append(
                        {
                            "type": "thinking",
                            "content": block.thinking,
                            "iteration": iteration + 1,
                        }
                    )
                elif block.type == "redacted_thinking":
                    final_blocks.append(
                        {
                            "type": "redacted_thinking",
                            "content": "[Thinking content redacted]",
                            "iteration": iteration + 1,
                        }
                    )
                elif block.type == "text":
                    final_blocks.append(
                        {
                            "type": "text",
                            "content": block.text,
                            "iteration": iteration + 1,
                        }
                    )

            response_blocks.extend(final_blocks)
            print(f"Added {len(final_blocks)} final blocks to response")

        print("\n--- Response chain handling complete ---")
        print(f"Total response blocks: {len(response_blocks)}")
        print(f"Total iterations: {iteration + 1}")

        return {
            "blocks": response_blocks,
            "stop_reason": response.stop_reason,
            "total_iterations": iteration + 1,
        }

    def _execute_tool(self, tool_name, tool_input):
        """Execute a tool and return the result."""
        print(f"\n+++ EXECUTING TOOL: {tool_name} +++")
        print(f"Tool input: {tool_input}")
        print(f"Tool input type: {type(tool_input)}")

        try:
            if tool_name == "analyze_user_account":
                print(f"MOCK USER DATA: {mock_user_data[0]}")
                result = analyze_user_account()
                # Return structured artifact for frontend
                user_analysis_data = result.model_dump()

                # Calculate summary metrics from account data
                total_balance = 0
                for account in user_analysis_data.get("account_analysis", []):
                    # Extract balance from analysis string
                    analysis = account.get("analysis", "")
                    balance_match = re.search(r"balance \$?([\d,]+\.?\d*)", analysis)
                    if balance_match:
                        balance = float(balance_match.group(1).replace(",", ""))
                        total_balance += balance
                        account["balance"] = balance

                    # Extract counts from analysis string
                    expense_match = re.search(r"(\d+) expenses?", analysis)
                    if expense_match:
                        account["expense_count"] = int(expense_match.group(1))

                    deposit_match = re.search(r"(\d+) deposits?", analysis)
                    if deposit_match:
                        account["deposit_count"] = int(deposit_match.group(1))

                user_analysis_data["total_balance"] = total_balance
                user_analysis_data["total_accounts"] = len(
                    user_analysis_data.get("account_analysis", [])
                )

                print(f"Structured user analysis data: {user_analysis_data}")
                return {"user_analysis": user_analysis_data}
            elif tool_name == "analyze_results":
                result = analyze_results(tool_input["results"])
                # Return the ToolResultsAnalysis object as a dict for JSON serialization
                return {"analysis_results": result.model_dump()}
            print("Executing Composio tool for non-weather request")
            print(f"User ID: {self.user_id}")
            composio = Composio()
            result = composio.tools.execute(
                slug=tool_name,
                user_id=self.user_id,
                arguments=tool_input,
            )
            print(f"Raw Composio result: {result}")
            print(f"Composio result type: {type(result)}")

            # Parse results using appropriate parser based on tool name
            if "finance" in tool_name.lower():
                parsed_result = parse_composio_finance_search_results(result)
                print("Used finance search parser")
            elif "news" in tool_name.lower():
                parsed_result = parse_composio_news_search_results(result)
                print("Used news search parser")
            elif "event" in tool_name.lower():
                parsed_result = parse_composio_event_search_results(result)
                print("Used event search parser")
            else:
                # Default to general search parser
                parsed_result = parse_composio_search_results(result)
                print("Used general search parser")

            print(f"Parsed result: {parsed_result}")
            return {"search_results": parsed_result}

        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            print("!!! TOOL EXECUTION EXCEPTION !!!")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            import traceback

            print(f"Traceback: {traceback.format_exc()}")
            return {"error": error_msg}
