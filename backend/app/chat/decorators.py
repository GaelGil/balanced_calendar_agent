from functools import wraps
from flask import session, redirect, url_for
from app.calendar.services import CalendarService
from app.chat.services import ChatService
from app.calendar.utils import load_credentials, save_credentials


def chat_calendar_service_required(f):
    """Decorator to require valid CalendarService."""

    @wraps(f)
    def decorated(*args, **kwargs):
        # get user ID
        user_id = session.get("user_id")
        # if no user ID, return error
        if not user_id:
            return redirect(url_for("auth.login"))
        # create CalendarService
        calendar_service = CalendarService(user_id, load_credentials, save_credentials)

        try:
            # validate credentials
            _ = calendar_service.get_service()  # this ensures creds are valid
        except ValueError:
            return redirect(url_for("calendar.authorize_calendar"))
        chat_service = ChatService(calendar_service)
        return f(chat_service, *args, **kwargs)

    return decorated
