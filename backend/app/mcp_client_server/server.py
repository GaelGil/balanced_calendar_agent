from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(Path("../.env"))


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
def search_event_brite_events(month: str, location: str) -> list[dict]:
    pass


@mcp.tool(
    name="search_luma_events",
    description="Search for events on eventbrite on a selected month",
)
def search_luma_events(month: str, location: str) -> list[dict]:
    pass


@mcp.tool(
    name="analyze_events",
    description="Analyzes the provided events to see which are the most relevant",
)
def analyze_events(events: list[dict]) -> list[dict]:
    """Saves the provided text to a .txt file."""
    pass


@mcp.tool(
    name="analyze_calender",
    description="Analyze the events on the google calendar",
)
def analyze_calendar(calendar: list[dict]) -> str:
    """"""
    pass


@mcp.tool(
    name="create_google_event",
    description="Create an event on google calendar",
)
def create_google_event(event: dict) -> str:
    """"""
    pass


@mcp.tool(
    name="update_calendar_event",
    description="Update an event on google calendar",
)
def assemble_content(calendar: list[dict]) -> str:
    """"""
    pass


# Run the server
if __name__ == "__main__":
    mcp.run(transport="sse")
