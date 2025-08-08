import os
import json
import datetime
from flask import (
    Blueprint,
    session,
    redirect,
    request,
    url_for,
    jsonify,
    current_app,
    Response,
)
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from app.calender.services import CalenderService

calendar = Blueprint("calendar", __name__)
calender_service = CalenderService()
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CLIENT_SECRETS_FILE = os.path.join(os.getcwd(), "credentials.json")


def save_credentials(user_id, creds: Credentials):
    """Persist creds.to_json() somewhere safe (DB, file per user, etc.)"""
    os.makedirs("tokens", exist_ok=True)
    with open(f"tokens/{user_id}.json", "w") as f:
        f.write(creds.to_json())


def load_credentials(user_id) -> Credentials | None:
    path = f"tokens/{user_id}.json"
    if not os.path.exists(path):
        return None
    return Credentials.from_authorized_user_file(path, SCOPES)


@calendar.route("/calendar/authorize")
def authorize_calendar():
    """Step 1: redirect user to Google’s consent screen."""
    if not os.path.exists(CLIENT_SECRETS_FILE):
        return jsonify({"error": "Missing credentials.json"}), 500

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("calendar.oauth2callback", _external=True),
    )
    auth_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    session["oauth_state"] = state
    return redirect(auth_url)


@calendar.route("/calendar/oauth2callback")
def oauth2callback():
    """Step 2: handle Google’s redirect back to us with a code."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=session.pop("oauth_state"),
        redirect_uri=url_for("calendar.oauth2callback", _external=True),
    )
    flow.fetch_token(code=request.args.get("code"))
    creds = flow.credentials

    # Save tied to current user
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No logged-in user"}), 401
    save_credentials(user_id, creds)

    frontend_url = current_app.config["FRONTEND_URL"]
    return redirect(f"{frontend_url}/calendar?connected=true")


@calendar.route("/calendar/events")
def list_events():
    """Fetch and return next 30 events, redirect to auth if needed."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    creds = load_credentials(user_id)
    if not creds:
        # No credentials yet → start auth flow
        return redirect(url_for("calendar.authorize_calendar"))

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_credentials(user_id, creds)
        else:
            # No valid refresh → start auth flow
            return redirect(url_for("calendar.authorize_calendar"))

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
    return jsonify(events_result.get("items", []))


@calendar.route("/calendar/status")
def calendar_status():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"connected": False}), 401

    creds = load_credentials(user_id)
    if creds and creds.valid:
        return jsonify({"connected": True})
    else:
        return jsonify({"connected": False})


@calendar.route("/calendar/stream", methods=["POST"])
def send_message_stream():
    """Send a message to the AI agent and get a streaming SSE response."""
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        def generate():
            try:
                # Stream blocks from the agent
                for event_data in calender_service.process_message_stream(message):
                    yield f"data: {json.dumps(event_data)}\n\n"
            except Exception as e:
                error_event = {"type": "error", "error": str(e)}
                yield f"data: {json.dumps(error_event)}\n\n"

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
            },
        )

    except Exception as e:
        return jsonify({"error": f"Failed to process message: {str(e)}"}), 500
