from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path("../.env"))


ARXIV_NAMESPACE = "{http://www.w3.org/2005/Atom}"
LLM = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = get_logger(__name__)


mcp = FastMCP(
    name="Knowledge Base",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)


@mcp.tool(
    name="search_event_brite_events",
    description="Search for events on eventbrite on a selected month",
)
def search_event_brite_events(month: str) -> list[dict]:
    pass


@mcp.tool(
    name="search_luma_events",
    description="Search for events on eventbrite on a selected month",
)
def search_luma_events(month) -> list[dict]:
    pass


@mcp.tool(
    name="save_txt",
    description="Save text to a .txt file",
)
def analyze_events(events: list[dict]) -> list[dict]:
    """Saves the provided text to a .txt file."""
    pass


@mcp.tool(
    name="writer_tool",
    description="Writes an essay on a given topic",
)
def writer_tool(query: str, context: str) -> str:
    """"""
    pass


@mcp.tool(
    name="review_tool",
    description="Reviews content on a given topic",
)
def review_tool(content: str, context: str) -> str:
    """"""
    pass


@mcp.tool(
    name="assemble_content",
    description="Assamble content from previous tools (context) and current content state",
)
def assemble_content(content: str, context: str) -> str:
    """"""
    pass


@mcp.tool(name="arxiv_search", description="Search arxiv")
def arxiv_search(query: str) -> str:
    pass


# Run the server
if __name__ == "__main__":
    mcp.run(transport="sse")
