from functools import wraps
from flask import session, redirect, url_for
from app.calendar.services import CalendarService
from app.calendar.utils import load_credentials, save_credentials


def calendar_service_required(f):
    """Decorator to require valid CalendarService."""

    @wraps(f)
    def decorated(*args, **kwargs):
        # get user ID
        user_id = session.get("user_id")
        # if no user ID, return error
        if not user_id:
            return redirect(url_for("auth.login"))
        # create CalendarService
        calender_service = CalendarService(user_id, load_credentials, save_credentials)

        return f(calender_service, *args, **kwargs)

    return decorated
