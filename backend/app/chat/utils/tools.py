from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
import datetime
from googleapiclient.discovery import build

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)  # logging stuff
logger = logging.getLogger(__name__)
load_dotenv(Path("../../.env"))  # load env
EVENT_BRITE_EVENTS = {}
LUMA_EVENTS = {}
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_events_in_month(creds) -> str:
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    """Fetch and return next 30 events, redirect to auth if needed."""

    service = build("calendar", "v3", credentials=creds)
    now = datetime.datetime.now(datetime.timezone.utc)
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            maxResults=30,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])


def analyze_events(calendar: list[dict], strict: bool) -> str:
    response = llm.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "developer",
                "content": f"""
                        You are an expert work life balancer, You take in a list of events in a calendar and determine if the events are overwhelimingly work. 
                        You MUST analyzse each event and determine this yourself.
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

                        Additionaly take note of calendar events that are not work related.
                        This way we can keep a idea of what user likes to do
                        

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


def calendar_availability(month: str) -> str:
    return f"Eventbrite events in {month}"


def create_new_calendar_event(event: dict) -> str:
    # event = service.events().insert(calendarId="primary", body=event).execute()
    # print(f"Event Created: {event.get('htmlLink')}")
    return f"New calendar event in {event}"
