import os
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def save_credentials(user_id: str, creds: Credentials) -> None:
    """Persist creds to tokens folder."""
    os.makedirs("tokens", exist_ok=True)  # create tokens folder
    with open(f"tokens/{user_id}.json", "w") as f:  # open file
        f.write(creds.to_json())  # write creds to file


def load_credentials(user_id: str) -> Credentials | None:
    """Load creds from tokens folder."""
    path = f"tokens/{user_id}.json"  # path to tokens
    if not os.path.exists(path):  # check if file exists
        return None  # return None if file does not exist
    return Credentials.from_authorized_user_file(path, SCOPES)  # return creds
