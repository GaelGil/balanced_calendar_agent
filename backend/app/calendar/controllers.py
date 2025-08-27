from flask import Blueprint, session, redirect, request, url_for, jsonify, current_app
from google_auth_oauthlib.flow import Flow
from app.auth.decorators import login_required
from app.calendar.utils import save_credentials
from app.calendar.decorators import calendar_service_required
from app.calendar.services import CalendarService
from app.calendar.utils import SCOPES, CLIENT_SECRETS_FILE

calendar = Blueprint("calendar", __name__)


@calendar.route("/calendar/authorize")
@login_required
@calendar_service_required
def authorize_calendar(calendar_service: CalendarService):
    """Redirect user to Google consent screen."""
    session.pop("oauth_state", None)
    auth_url, state = calendar_service.auth_calendar()
    session["oauth_state"] = state

    # redirect to consent screen
    return redirect(auth_url)


@calendar.route("/calendar/oauth2callback")
@login_required
def oauth2callback():
    # set up OAuth 2.0 flow
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=session.pop("oauth_state"),
        redirect_uri=url_for("calendar.oauth2callback", _external=True),
    )
    # exchange auth code for credentials
    flow.fetch_token(code=request.args.get("code"))
    # store credentials
    creds = flow.credentials

    # get user ID
    user_id = session.get("user_id")
    # if no user ID, return error
    if not user_id:
        return jsonify({"error": "No logged-in user"}), 401
    # save credentials
    save_credentials(user_id, creds)
    # redirect to frontend
    frontend_url = current_app.config["FRONTEND_URL"]
    return redirect(f"{frontend_url}/calendar?connected=true")


@calendar.route("/calendar/events")
@login_required
@calendar_service_required
def list_events(calendar_service: CalendarService):
    events = calendar_service.get_events_in_month()
    return jsonify(events)


@calendar.route("/calendar/status")
@login_required
@calendar_service_required
def calendar_status(calendar_service: CalendarService):
    return jsonify({"connected": calendar_service.status()})
