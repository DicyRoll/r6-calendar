import logging
import os
from datetime import datetime

import requests
import dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError

from match import Match

dotenv.load_dotenv()

SCOPE = [os.environ.get("SCOPE")]
AUTH_PORT = int(os.environ.get("AUTH_PORT"))
CALENDAR_ID = os.environ.get("CALENDAR_ID")
CALENDAR_NAME = os.environ.get("CALENDAR_NAME")


def get_credentials() -> Credentials:
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPE)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPE)
            creds = flow.run_local_server(port=AUTH_PORT)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def create_r6_calendar(service: Resource) -> str:
    default_calendar = {"summary": CALENDAR_NAME, "timeZone": "Europe/Rome"}
    new_calendar = service.calendars().insert(body=default_calendar).execute()

    dotenv.set_key(dotenv.find_dotenv(), "CALENDAR_ID", new_calendar["id"])

    logging.info(f"Created calendar {new_calendar['id']} - {new_calendar['summary']}")
    return new_calendar["id"]


def main():
    logging.basicConfig(
        filename="app.log",
        format="[%(asctime)s]\n%(levelname)s: %(message)s",
        level=logging.INFO,
    )

    matches_to_add: list[Match] = []

    match_file = open("matches.txt", "r+")
    match_file_content = match_file.read()

    logging.info("Begin process")
    logging.info("Begin fetch procedure")
    for year in range(2020, datetime.now().year + 1):  # 2020
        logging.info(f"Fetching year {year}")
        for month in range(1, 13):
            logging.info(f"Fetching month {month}")

            response = requests.get(
                f"https://www.ubisoft.com/_next/data/JjLqCXwsalIA9VRj0ZW6W/en-us/esports/rainbow-six/siege/calendar/{year}-{month:02d}.json"
            )

            data = response.json()["pageProps"]["page"]

            for match_element in data["matches"]:
                match = Match(
                    match_element["competition"]["name"],
                    (match_element["team1"]["name"], match_element["team2"]["name"]),
                    match_element["timestamp"],
                )

                if match.id not in match_file_content:
                    if match.validate_match():
                        matches_to_add.append(match)
                        match_file.write(match.id + "\n")
                    else:
                        logging.warning(f"Match {match} is invalid")

    match_file.close()
    logging.info("End of fetch process")

    creds = get_credentials()
    try:
        service = build("calendar", "v3", credentials=creds)
        calendar_list = service.calendarList().list().execute()

        calendar_id = None
        if not calendar_list["items"]:
            calendar_id = create_r6_calendar(service)
        else:
            for calendar in calendar_list["items"]:
                if calendar["id"] == CALENDAR_ID:
                    calendar_id = calendar["id"]
                    break

            if not calendar_id:
                calendar_id = create_r6_calendar(service)

        for match in matches_to_add:
            match_event = {
                "summary": match.summary,
                "start": {
                    "dateTime": match.start_time.isoformat(),
                    "timeZone": "Europe/Rome",
                },
                "end": {
                    "dateTime": match.end_time.isoformat(),
                    "timeZone": "Europe/Rome",
                },
            }

            service.events().insert(calendarId=calendar_id, body=match_event).execute()
            logging.info(f"Added event {match}")
    except HttpError as error:
        logging.error(f"Error adding event: {error}")

    logging.info("End process")


if __name__ == "__main__":
    main()
