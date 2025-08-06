"""
Agent workflow for processing task requests

This script reads takes in a user request and uses a planner agent to create a plan
to complete the request. The plan is then executed by an executor.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from typing import Tuple
from agent.utils.OpenAIClient import OpenAIClient
from agent.mcp_client_server.client import MCPClient
from agent.utils.Executor import Executor
from agent.PlannerAgent import PlannerAgent
from agent.utils.prompts import PLANNER_AGENT_PROMPT
from agent.utils.schemas import Plan

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def initialize_agent_service() -> Tuple[Executor, PlannerAgent, MCPClient]:
    """Initialize and return the OrchestratorAgent with MCP client integration.

    Returns:
        Tuple[OrchestratorAgent, MCPClient]: A tuple containing the initialized OrchestratorAgent and MCPClient.
    """
    try:
        logger.info("Initializing MCP client ...")
        mcp_client = MCPClient()
        await mcp_client.connect()

        logger.info("Getting tools from MCP ...")
        tools = await mcp_client.get_tools()
        logger.info(f"Loaded {len(tools)} tools from MCP")

        logger.info("Initializing OpenAI client ...")
        # openai_client = OpenAI(os.getenv("OPENAI_API_KEY"))
        llm = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY")).get_client()

        # Ensure tools is a list and log its structure
        if not isinstance(tools, list):
            logger.warning(
                f"Tools is not a list, converting to list. Type: {type(tools)}"
            )
            tools = [tools] if tools is not None else []

        logger.info("Initializing Executor ...")
        logger.info(f"Number of tools: {len(tools)}")

        try:
            # Create a copy of tools to avoid modifying the original
            agent_tools = [
                tool.copy() if hasattr(tool, "copy") else tool for tool in tools
            ]
            # Initialize Executor
            executor = Executor(mcp_client=mcp_client)
            logger.info("Successfully initialized Executor")
            # Initialize PlannerAgent
            planner = PlannerAgent(
                dev_prompt=PLANNER_AGENT_PROMPT,
                llm=llm,
                messages=[],
                tools=agent_tools,
                model_name="gpt-4.1-mini",
            )
            logger.info("Successfully initialized PlannerAgent")
            return executor, planner, mcp_client

        except Exception as agent_init_error:
            logger.error(
                f"Error initializing OrchestratorAgent: {str(agent_init_error)}"
            )
            logger.error(
                f"Agent initialization error type: {type(agent_init_error).__name__}"
            )
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    except Exception as e:
        logger.error(f"Failed to initialize agent service: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


async def create_execute_plan(
    executor: Executor, planer: PlannerAgent, content: str
) -> bool:
    """
    Process a single email file and place orders based on its content using the agentic workflow.
    Args:
        agent: Initialized OrchestratorAgent
        mcp_client: Initialized MCPClient
        file_path: Path to the email file to process
    Returns:
        bool: True if processing was successful, False otherwise
    """
    # Try to process the email using agent
    try:
        plan = planer.plan(content)  # create a plan

        plan_parsed: Plan = plan.output_parsed  # parse the plan
        logger.info(f"Created plan: {plan_parsed}")

        res = await executor.execute_plan(plan_parsed)  # execute the plan
        logger.info(f"Execution results: {res}")
    except Exception as process_error:  # Exception as process_error
        logger.error(
            f"Error in agentic email processing: {str(process_error)}", exc_info=True
        )
        return False


async def run_agent() -> None:
    """ """

    # Initialize agent service
    query = "Balance this calender to ensure a healthy work life balance"
    try:
        orchestrator, planner, mcp_client = await initialize_agent_service()
        await create_execute_plan(orchestrator, planner, query)
    except Exception as e:
        logger.error(f"Error in email processing workflow: {str(e)}")
    finally:
        # Clean up
        if "mcp_client" in locals():
            await mcp_client.disconnect()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(run_agent())
