from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger
from openai import OpenAI
from dotenv import load_dotenv
from app.chat.agent.mcp_client_server.sources.event_brite_events import (
    EVENT_BRITE_EVENTS,
)
from app.chat.agent.mcp_client_server.sources.luma_events import LUMA_EVENTS

# from pathlib import Path
import os

load_dotenv()
# run using python -m MCP.server

ARXIV_NAMESPACE = "{http://www.w3.org/2005/Atom}"
LLM = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = get_logger(__name__)


mcp = FastMCP(
    name="Knowledge Base",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)


@mcp.tool(
    name="get_calender_by_month",
    description="Get users calendar by month",
)
def get_calender_by_month(month: str) -> str:
    return f"Calendar for month {month}"


@mcp.tool(
    name="get_events_by_month",
    description="Get the users events by month",
)
def get_events_by_month(calendar: list[dict]) -> str:
    return f"Events for month {calendar}"


@mcp.tool(
    name="analyze_events",
    description="Analyze the type of events in the calendar",
)
def analyze_events(calendar: list[dict], strict: bool) -> str:
    response = LLM.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "developer",
                "content": f"""
                        You are an expert work life balancer, You take in a list of events in a calendar and determine if the events are overwhelimingly work. 
                        You MUST analyzse each event and determine this
                        After determining the type of event, you must write a proposed solution for the user to take action on.
                        Ex: You have too many work events. Lets balance the work and non work events.
                        If you determine events are balanced enough, you MUST write a response that is positive and encouraging.
                        Example: great job! You have a balanced work life.

                        Here is an example of a calendar:

                        Here is a list of events in the calendar:
                        
                        event_id: 1
                        event_title: Title
                        event_duration: 2 hours
                        event_location: Location
                        event_description: Description

                        ...
                        
                        event_id: n
                        event_title: Title
                        event_duration: 2 hours
                        event_location: Location
                        event_description: Description

                        
                        YOU MUST USE THE CALENDAR PROVIDED TO INFORM YOUR RESPONSE
                        
                        Here is the Calendar: {calendar}
                        """,
            },
            {
                "role": "user",
                "content": "Ensure my calendar events are equal wellness events and work",
            },
        ],
    )

    return response


@mcp.tool(
    name="search_luma_events",
    description="Search for events on Luma",
)
def search_luma_events(month: str) -> str:
    events = LUMA_EVENTS[month]
    for i in range(len(events)):
        print(f"Event {i}: {events[i]}")
        # check if event is already in calendar
        # check if event fits in time slot
        # add to list of events for user to review
    return f"Eventbrite events in {month}"


@mcp.tool(
    name="search_eventbrite_events",
    description="Search for events on Eventbrite",
)
def search_eventbrite_events(month: str) -> str:
    events = EVENT_BRITE_EVENTS[month]
    for i in range(len(events)):
        print(f"Event {i}: {events[i]}")
        # check if event is already in calendar
        # check if event fits in time slot
        # add to list of events for user to review
    return f"Eventbrite events in {month}"


@mcp.tool(
    name="calendar_availability",
    description="search calendar availability",
)
def calendar_availability(month: str) -> str:
    return f"Eventbrite events in {month}"


@mcp.tool(
    name="cretae_new_calendar_event",
    description="Create a new calendar event",
)
def create_new_calendar_event(event: dict) -> str:
    # event = service.events().insert(calendarId="primary", body=event).execute()
    # print(f"Event Created: {event.get('htmlLink')}")
    return f"New calendar event in {event}"


# Run the server
if __name__ == "__main__":
    mcp.run(transport="sse")
