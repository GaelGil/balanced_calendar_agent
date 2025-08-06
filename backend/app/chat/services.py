from composio import Composio  # type: ignore
from app.chat.agent.PlannerAgent import PlannerAgent  # type: ignore
from app.chat.agent.utils.prompts import PLANNER_AGENT_PROMPT
from app.chat.agent.utils.OpenAIClient import OpenAIClient
from app.chat.agent.mcp_client_server.client import MCPClient
from app.chat.agent.utils.Executor import Executor
from app.chat.agent.utils.schemas import InitialResponse
from openai import OpenAI
from dotenv import load_dotenv

# from typing import Tuple
from pathlib import Path
import os

load_dotenv(Path("../../.env"))


class ChatService:
    def __init__(self):
        self.planner: PlannerAgent = None
        self.mcp_client: MCPClient = None
        self.llm: OpenAI = None
        self.tools = None
        self.model_name: str = "gpt-4.1-mini"
        self.composio = Composio()
        self.user_id = "0000-1111-2222"

    async def process_message(self, user_message):
        """
        Process a user message using the agent's multiple_tool_calls_with_thinking logic.
        Returns structured response data for the frontend.
        """
        print("Initializing MCP client ...")
        self.mcp_client = MCPClient()
        await self.mcp_client.connect()

        print("Getting tools from MCP ...")
        self.tools = await self.mcp_client.get_tools()
        print(f"Loaded {len(self.tools)} tools from MCP")
        print(f"Tools: {self.tools} \n")
        print("\n=== CHAT SERVICE: Processing new message ===")
        print(f"User message: {user_message}")
        print(f"Model: {self.model_name}")

        print("Initializing OpenAI client ...")
        self.llm = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY")).get_client()

        print("Initializing Planner Agent ...")
        self.planner = PlannerAgent(
            dev_prompt=PLANNER_AGENT_PROMPT,
            llm=self.llm,
            messages=[],
            tools=self.tools,
            model_name="gpt-4.1-mini",
        )

        try:
            # Initial request (same structure as agent.py)
            print("\n--- Making initial API call to Claude ---")

            response = self.llm.responses.parse(
                model=self.model_name,
                input=[{"role": "user", "content": user_message}],
                text_format=InitialResponse,
            )

            print(f"Initial response content blocks: {len(response.output)}")

            # Process the response and handle tool calls
            conversation_history = [{"role": "user", "content": user_message}]
            print(
                f"Starting conversation history with {len(conversation_history)} messages"
            )
            # create a plan
            plan = self.planner.plan(user_message)
            plan_parsed = plan.output_parsed
            final_response = await self._handle_response_chain(
                plan_parsed, response, conversation_history
            )

            print("\n=== CHAT SERVICE: Processing complete ===")

            return {"success": True, "response": final_response}

        except Exception as e:
            print("\n!!! CHAT SERVICE ERROR !!!")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            import traceback

            print(f"Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    async def _handle_response_chain(self, plan, response, conversation_history):
        """
        Handle the full response chain including tool calls, following agent.py logic.
        Returns structured response data.
        """
        executor = Executor(self.mcp_client)
        print("\n--- Starting response chain handling ---")
        # response_blocks = []
        # iteration = 0

        res: list[dict] = await executor.execute_plan(plan)

        return res[-1]["results"]
