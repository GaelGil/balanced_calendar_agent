from flask import Flask, redirect, request, session, jsonify
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from flask import Blueprint
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path("../.env"))

app = Flask(__name__)
app.secret_key = "super-secret-key"  # Change this

# Load client config from environment or file
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# This URL must match what you set in Google console
REDIRECT_URI = "http://localhost:5000/auth/google/callback"

calendar = Blueprint("calendar", __name__)


@calendar.route("/auth/google")
def auth_google():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    auth_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    session["state"] = state
    return redirect(auth_url)


@calendar.route("/auth/google/callback")
def auth_google_callback():
    state = session.get("state", None)
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI,
    )

    # ✅ Fetch the token first
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # ✅ Then store it once in session
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    # ✅ Optionally redirect to frontend after login
    return redirect("http://localhost:5173")


@calendar.route("/calendar/events")
def get_calendar_events():
    if "credentials" not in session:
        return jsonify({"error": "User not authenticated"}), 401

    creds_data = session["credentials"]
    creds = Credentials(
        token=creds_data["token"],
        refresh_token=creds_data.get("refresh_token"),
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data["scopes"],
    )

    # If token expired, refresh automatically
    if creds.expired and creds.refresh_token:
        creds.refresh(requests.Request())

    # Call Google Calendar API
    response = requests.get(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        headers={"Authorization": f"Bearer {creds.token}"},
    )

    events = response.json()
    return jsonify(events)
