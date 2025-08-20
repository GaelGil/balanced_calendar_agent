from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
import datetime
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# logging stuff
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# load env
load_dotenv(Path("../../.env"))
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_events_in_next_days(days: int) -> str:
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("./token.json"):
        creds = Credentials.from_authorized_user_file("./token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "./credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        print(f"Getting the upcoming {days} events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=days,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred: {error}")
    return events


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
