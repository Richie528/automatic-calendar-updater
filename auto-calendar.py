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
dates = []

def getDates():
    urlFile = open(sys.path[0] + '/../super-secret-url.txt')
    requestUrl = urlFile.readline()
    r = requests.get(requestUrl, headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'})
    c = "dTddCR"
    soup = BeautifulSoup(r.content, "html.parser")

    dateElements = soup.find_all("span", class_=c)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for dateElement in dateElements:
        dates.append(dateElement.text)

    for i in range(0, len(dates)):
        parts = dates[i].split(", ")
        for j in range(0, len(parts)):
            parts[j] = parts[j].split(" ")

        year = int(2000 + int(parts[2][2]))
        month = months.index(parts[2][1]) + 1
        day = int(parts[2][0])
        hour = parts[0][0]
        if parts[0][1] == 'PM':
            hour = hour.split(":")
            hour[0] = int(hour[0]) % 12
            hour[0] += 12
            hour = ":".join([str(hour[0]), str(hour[1])])

        end = hour
        end = end.split(":")
        end[0] = str(int(end[0]) + 1)
        end = ":".join(end)

        dates[i] = [year, month, day, hour, end]

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
        startTime = str(date[0]) + "-"  + str(date[1]) + "-" + str(date[2]) + "T" + date[3] + ":00" + utc
        endTime =  str(date[0]) + "-"  + str(date[1]) + "-" + str(date[2]) + "T" + date[4] + ":00" + utc
        # make the event :D
        event = {
            "summary": "Basketball",
            "colorId": 3,
            "start": {"dateTime": startTime},
            "end": {"dateTime": endTime}
        }
        event = service.events().insert(calendarId="primary", body=event).execute()
        print("Event created " + event.get('htmlLink'))


getDates()
createEvents()