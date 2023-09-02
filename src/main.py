import logging
import os
import re
from datetime import datetime

import dotenv
import requests
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from requests import JSONDecodeError

from match import Match

# set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

dotenv.load_dotenv()

SCOPE = [os.environ.get("SCOPE")]
CALENDAR_ID = os.environ.get("CALENDAR_ID")
CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH")


def get_google_service() -> Resource:
    if os.path.exists(CREDENTIALS_PATH):
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_PATH, SCOPE
        )
    else:
        err_msg = f"Credentials file {CREDENTIALS_PATH} does not exist"
        logging.error(err_msg)
        raise FileNotFoundError(err_msg)

    return build("calendar", "v3", credentials=creds)


def main():
    logging.basicConfig(
        filename="logs/app.log",
        format="[%(asctime)s]\n%(levelname)s: %(message)s",
        level=logging.INFO,
    )

    matches_to_add: list[Match] = []

    if os.path.exists("matches.txt"):
        match_file = open("matches.txt", "r+")
        match_file_content = match_file.read()
    else:
        match_file = open("matches.txt", "a")
        match_file_content = ""

    logging.info("Begin process")
    logging.info("Begin fetch procedure")

    calendar_page = requests.get(
        "https://www.ubisoft.com/en-us/esports/rainbow-six/siege/calendar"
    )
    calendar_page_id = re.findall(
        '(?<="buildId":")([a-zA-Z0-9_-]+)(?=")', calendar_page.text
    ).pop()

    for year in range(2020, datetime.now().year + 1):
        logging.info(f"Fetching year {year}")
        for month in range(1, 13):
            logging.info(f"Fetching month {month}")
            response = requests.get(
                f"https://www.ubisoft.com/_next/data/{calendar_page_id}/en-us/esports/rainbow-six/siege/calendar/{year}-{month:02d}.json"
            )

            try:
                data = response.json()["pageProps"]["pageData"]

                for match_element in data["matches"]:
                    match = Match(
                        match_element["competition"]["name"],
                        (
                            match_element["team1"]["name"],
                            match_element["team2"]["name"],
                        ),
                        match_element["timestamp"],
                    )

                    if match.id not in match_file_content:
                        if match.validate_match():
                            matches_to_add.append(match)
                            match_file.write(match.id + "\n")
                        else:
                            logging.warning(f"Match {match} is invalid")
            except JSONDecodeError:
                logging.warning(f"Response for {year}-{month} does not have valid JSON")

    match_file.close()
    logging.info("End of fetch process")

    if len(matches_to_add) > 0:
        service = get_google_service()

        # check if calendar exists
        calendar = service.calendars().get(calendarId=CALENDAR_ID).execute()
        if not calendar:
            err_msg = f"Calendar {CALENDAR_ID} does not exist"
            logging.error(err_msg)
            raise Exception(err_msg)

        for match in matches_to_add:
            try:
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

                service.events().insert(
                    calendarId=CALENDAR_ID, body=match_event
                ).execute()
                logging.info(f"Added event {match}")
            except HttpError as error:
                logging.error(f"Error adding event: {error}")

        logging.info("End process")


if __name__ == "__main__":
    main()
