from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
from app.chat.utils.prompts import ANALYSE_EVENTS_PROMPT
from app.chat.utils.schemas import EventsAnalyzed

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)  # logging stuff
logger = logging.getLogger(__name__)
load_dotenv(Path("../../.env"))  # load env
EVENT_BRITE_EVENTS = {}
LUMA_EVENTS = {}
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_events(events: str) -> EventsAnalyzed:
    """Analyzes the events in the calendar and returns a summary of the events.

    Args:
        calendar (list[dict]): A list of events in the calendar.

    Returns:
        EventsAnalyzed: A analysis of the events in the calendar.
    """
    # Create the input for the model
    messages = [
        {
            "role": "developer",
            "content": f""" {ANALYSE_EVENTS_PROMPT}
                    Here is the events: {events}
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
        text_format=EventsAnalyzed,
    )

    # Return the response
    return response.output_parsed
