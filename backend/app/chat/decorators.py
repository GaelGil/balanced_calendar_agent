from functools import wraps
from flask import session, redirect, url_for
from app.calendar.services import CalendarService
from app.chat.services import ChatService
from app.calendar.utils import load_credentials, save_credentials


def chat_calendar_service_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("auth.login"))

        calendar_service = CalendarService(user_id, load_credentials, save_credentials)
        try:
            _ = calendar_service.get_service()
        except ValueError:
            return redirect(url_for("calendar.authorize_calendar"))

        # Get existing chat_session_id from Flask session
        chat_session_id = session.get("chat_session_id")

        # Create or load ChatService
        chat_service = ChatService(
            user_id=user_id,
            calendar_service=calendar_service,
            session_id=chat_session_id,
        )

        # Store session_id in Flask session for future requests
        session["chat_session_id"] = chat_service.session_id

        return f(chat_service, *args, **kwargs)

    return decorated
