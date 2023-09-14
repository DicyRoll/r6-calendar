# Rainbow 6 Siege Esports Google Calendar
This Python script updates a Google Calendar with upcoming Rainbow 6 Siege esports matches, which are also available on the [official Ubisoft calendar site](https://www.ubisoft.com/en-us/esports/rainbow-six/siege/calendar).

## Adding the Calendar to your Google Account

To add the Google Calendar to your account, simply click on [this link](https://calendar.google.com/calendar/u/3?cid=MmE1MGQ0MzY5ZjFlZmEwNjI4M2Q1Y2ZlODNhM2M3MGQ5MDc2MTYyZGI3MmU2NzU4NGI3YjA4MWE0MThmNjE2Y0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t) and then click on "Add".

The calendar is currently updated 3 times a day.

---

## Requirements

- Docker
- A Google Cloud Platform project with the Calendar API enabled and a service account set up.

## Setup
1. Clone this repository to your local machine.
2. Open the repository in Visual Studio Code with the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension installed.
3. Choose "Reopen in Container" in the prompt that appears.
4. Download your Google Cloud service account credentials and place them in the `src` directory
5. Share your calendar with the service account by adding the service account's email address as a shared user to the calendar.
6. Create a `.env` file using the `.env.example` file as reference.
7. Run the `main.py` script
