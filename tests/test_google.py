from __future__ import print_function

import async_sched
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


DEFAULT_TIME = datetime.time(hour=6, minute=30, second=0)


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def get_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def create_event(summary, start_on=None, end_on=None, attendees=None, **kwargs):
    event = kwargs.copy()

    event['summary'] = summary

    if start_on is None:
        start_on = datetime.datetime.today().replace(hour=DEFAULT_TIME.hour, minute=DEFAULT_TIME.minute,
                                                     second=DEFAULT_TIME.second)
    if end_on is None:
        end_on = start_on + datetime.timedelta(hours=1)

    event['start'] = {
        'dateTime': str(start_on.isoformat()),
        'timeZone': 'America/New_York',
        }
    event['end'] = {
        'dateTime': str(end_on.isoformat()),
        'timeZone': 'America/New_York',
        }

    if attendees:
        if not isinstance(attendees, list):
            attendees = [attendees]
        event['attendees'] = attendees  # [{'email': 'teachmmorgan3@gmail.com'}]

    # event['recurrence'] = [
    #     'RRULE:FREQ=DAILY;COUNT=3'  # INTERVAL=3, COUNT is total
    #     ]
    #
    # 'reminders': {
    #     'useDefault': False,
    #     'overrides': [
    #         {'method': 'email', 'minutes': 24 * 60},
    #         {'method': 'popup', 'minutes': 10},
    #         ],
    #     },

    return event


def add_event(summary, start_on=None, end_on=None, attendees=None, **kwargs):
    service = get_service()
    event = create_event(summary, start_on=start_on, end_on=end_on, attendees=attendees, **kwargs)
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    return event


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """



if __name__ == '__main__':
    main()
