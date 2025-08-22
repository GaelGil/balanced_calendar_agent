import os
import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CLIENT_SECRETS_FILE = os.path.join(os.getcwd(), "credentials.json")


class CalendarService:
    def __init__(self, user_id, creds_loader, creds_saver):
        """
        user_id: ID of the logged-in user
        creds_loader: function to load Credentials from storage
        creds_saver: function to save Credentials to storage
        """
        self.user_id = user_id
        self.load_credentials = creds_loader
        self.save_credentials = creds_saver
        self.creds = self.load_credentials(user_id)

    def get_service(self):
        if not self.creds:
            raise ValueError("No credentials found")
        if not self.creds.valid:
            if self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                self.save_credentials(self.user_id, self.creds)
            else:
                raise ValueError("Credentials not valid, user must re-auth")
        return build("calendar", "v3", credentials=self.creds)

    def get_events_in_month(self):
        service = self.get_service()
        now = datetime.datetime.now(datetime.timezone.utc)
        start_of_month = now.replace(day=1)
        end_of_month = start_of_month.replace(month=now.month + 1) - datetime.timedelta(
            days=1
        )

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_of_month.isoformat(),
                timeMax=end_of_month.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events_result.get("items", [])

    def create_event(self, event):
        service = self.get_service()
        return service.events().insert(calendarId="primary", body=event).execute()

    def find_availability(self, start_time, end_time) -> list:
        """
        Return busy events between start_time and end_time.
        """
        service = self.get_service()
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])

    def find_free_slots(self, start_time, end_time) -> list:
        """
        Return free time slots between start_time and end_time.
        """
        busy_events = self.find_availability(start_time, end_time)

        # Sort events by start time
        busy_events.sort(
            key=lambda e: e["start"].get("dateTime", e["start"].get("date"))
        )

        free_slots = []
        current_start = start_time

        for event in busy_events:
            event_start_str = event["start"].get("dateTime") or event["start"].get(
                "date"
            )
            event_end_str = event["end"].get("dateTime") or event["end"].get("date")

            event_start = datetime.datetime.fromisoformat(event_start_str)
            event_end = datetime.datetime.fromisoformat(event_end_str)

            # If there's a gap before this event, it's free
            if current_start < event_start:
                free_slots.append(
                    {"start": current_start.isoformat(), "end": event_start.isoformat()}
                )

            # Move the current_start forward
            if event_end > current_start:
                current_start = event_end

        # After the last event, check if there's still free time
        if current_start < end_time:
            free_slots.append(
                {"start": current_start.isoformat(), "end": end_time.isoformat()}
            )

        return free_slots

    def status(self):
        return self.creds is not None and self.creds.valid
