from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
from app.chat.utils.prompts import ANALYSE_EVENTS_PROMPT

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)  # logging stuff
logger = logging.getLogger(__name__)
load_dotenv(Path("../../.env"))  # load env
EVENT_BRITE_EVENTS = {}
LUMA_EVENTS = {}
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_events(calendar: list[dict]) -> str:
    """Analyzes the events in the calendar and returns a summary of the events.

    Args:
        calendar (list[dict]): A list of events in the calendar.

    Returns:
        str: A summary of the events in the calendar.
    """
    # Create the input for the model
    messages = [
        {
            "role": "developer",
            "content": f""" {ANALYSE_EVENTS_PROMPT}
                    Here is the Calendar: {calendar}
                    """,
        },
        {
            "role": "user",
            "content": "Ensure my calendar events are equal wellness events and work",
        },
    ]

    # Get the response from the model
    response = llm.responses.parse(
        model="gpt-4.1-mini",
        input=messages,
    )

    # Return the response
    return response


def search_luma_events(month: str) -> str:
    events = LUMA_EVENTS[month]
    for i in range(len(events)):
        print(f"Event {i}: {events[i]}")
        # check if event is already in calendar
        # check if event fits in time slot
        # add to list of events for user to review
    return f"Eventbrite events in {month}"


def search_eventbrite_events(month: str) -> str:
    events = EVENT_BRITE_EVENTS[month]
    for i in range(len(events)):
        print(f"Event {i}: {events[i]}")
        # check if event is already in calendar
        # check if event fits in time slot
        # add to list of events for user to review
    return f"Eventbrite events in {month}"
