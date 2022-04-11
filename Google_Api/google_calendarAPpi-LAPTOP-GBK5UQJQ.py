from _TASKSAPI import Create_Service, convert_to_RFC_datetime
# to extend functionality check: https://www.thepythoncode.com/article/use-gmail-api-in-python
'''
    insert	Creates a new secondary calendar. By default, this calendar is also added to the creator's calendar list.	Inserts an existing calendar into the user's list.
    delete	Deletes a secondary calendar.	Removes a calendar from the user's list.
    get	Retrieves calendar metadata e.g. title, time zone.	Retrieves metadata plus user-specific customization such as color or override reminders.
'''
service = MainApplication(None).service_building()
location = None
description = None
dateTime_start = convert_to_RFC_datetime(2021,9,9,12,12)
dateTime_end = convert_to_RFC_datetime(2021,9,9,13,12)

attendees = {
    'email': 'uchekesla@gmail.com'
}

event1 = {
  'summary': 'Google I/O 2021',
  'location': location,
  'description': description,
  'start': {
    'dateTime': dateTime_start,
    'timeZone': 'America/Los_Angeles',
  },
  'end': {
    'dateTime': dateTime_end,
    'timeZone': 'America/Los_Angeles',
  },
  'recurrence': [
    'RRULE:FREQ=DAILY;COUNT=2'
  ],
  'attendees': [
      attendees
  ],
  'reminders': {
    'useDefault': False,
    'overrides': [
      {'method': 'email', 'minutes': 24 * 60},
      {'method': 'popup', 'minutes': 10},
    ],
  },
}

events_result = service.events().list(calendarId='primary', timeMin=dateTime_start,
                                    maxResults=10, singleEvents=True,
                                    orderBy='startTime').execute()
events = events_result.get('items', [])

if not events:
    print('No upcoming events found.')
for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    print(start, event['summary'])


event = service.events().insert(calendarId='primary', body=event1).execute()
print(event)