import datetime
import os.path
import sys
import requests
from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
utc = "+10:00"
eventName = "Basketball"
eventColour = 6

dates = []

def getDates():
    requestUrl = ""
    with open(sys.path[0] + '/../super-secret-url.txt') as f:
        requestUrl = f.readline()
    r = requests.get(requestUrl, headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'})
    soup = BeautifulSoup(r.content, "html.parser")

    c = "dTddCR" # the class that i want
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    dateElements = soup.find_all("span", class_=c) # all the elements that contain the dates and times i want

    for dateElement in dateElements:
        parts = dateElement.text.split(", ")
        for i in range(0, len(parts)):
            parts[i] = parts[i].split(" ")

        time = parts[0][0].split(":")
        if parts[0][1] == "PM":
            time[0] = str(int(time[0]) % 12 + 12)
        startTime = ":".join(time)
        endTime = ":".join([str(int(time[0]) + 1), time[1]])

        dates.append([
            "20" + parts[2][2], # year
            str(months.index(parts[2][1]) + 1).zfill(2), # month
            parts[2][0], # day
            startTime,
            endTime
        ])

def createEvents():
    # get credentials
    creds = None
    if os.path.exists(sys.path[0] + '/../token.json'):
        creds = Credentials.from_authorized_user_file(sys.path[0] + '/../token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(sys.path[0] + '/../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(sys.path[0] + '/../token.json', "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)

    # create event
    for date in dates:
        # calculate start and end times
        startTime = str(date[0]) + "-"  + str(date[1]) + "-" + str(date[2]) + "T" + date[3] + ":00" + utc
        endTime =  str(date[0]) + "-"  + str(date[1]) + "-" + str(date[2]) + "T" + date[4] + ":00" + utc
        # remove pre-existing duplicates
        possibleDuplicates = (
            service.events().list
            (
                calendarId="primary",
                timeMin=startTime,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        possibleDuplicates = possibleDuplicates.get("items", [])
        for possibleDuplicate in possibleDuplicates:
            start = possibleDuplicate["start"].get("dateTime", possibleDuplicate["start"].get("date"))
            end = possibleDuplicate["end"].get("dateTime", possibleDuplicate["end"].get("date"))

            if (start == startTime and end == endTime):
                if (possibleDuplicate["summary"] == "Basketball"):
                    service.events().delete(calendarId = "primary", eventId = possibleDuplicate["id"]).execute()

        # make the event :D
        event = {
            "summary": eventName,
            "colorId": eventColour,
            "start": {"dateTime": startTime},
            "end": {"dateTime": endTime}
        }
        event = service.events().insert(calendarId="primary", body=event).execute()
        print("Event created: " + event.get('htmlLink'))

print("Creating your events...")
getDates()
createEvents()
print("Done!")