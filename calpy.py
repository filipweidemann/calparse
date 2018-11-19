import os
import caldav
from datetime import datetime, timedelta


class CalDavParser(caldav.DAVClient):
    def __init__(
        self, 
        url, 
        username, 
        password, 
        start_date, 
        end_date, 
        parse_list=[
            'SUMMARY', 
            'DESCRIPTION', 
            'LOCATION', 
            'DTSTART', 
            'DTEND'
        ], 
        single_calendar=False, 
        *args, 
        **kwargs
    ):
        super(CalDavParser, self).__init__(url, *args, **kwargs)
        self.calendar_url = url
        self.username = username
        self.password = password
        self.start_date = start_date
        self.end_date = end_date
        self.parse_list = parse_list
        self.is_single_calendar = single_calendar
        self.client = None
        self.principal = None

    def init_client(self):
        self.client = caldav.DAVClient(self.url, username=self.username, password=self.password)
        self.principal = self.client.principal()

    def get_events_by_date(self):
        if not self.start_date or not isinstance(self.start_date, datetime):
            raise ValueError('Cannot parse calendar events by date, missing value for attribute "start_date".')
        
        if not self.end_date or not isinstance(self.end_date, datetime):
            raise ValueError('Cannot parse calendar events by date, mising value for attribute "end_date".')
        
        calendars = [calendar if not self.is_single_calendar else caldav.objects.Calendar(client=self.client, url=self.url) for calendar in self.principal.calendars()]
 
        for calendar in calendars:
            events = []
            results = calendar.date_search(self.start_date, self.end_date)
            for event in results:
                parsed_event = {}
                for line in [stripped for stripped in event.data.replace('\r\n ', '').split('\r\n') 
                if stripped.strip()]:
                    key, value = line.split(':', 1)
                    if key in self.parse_list:
                        parsed_event[key] = value
                        events.append(parsed_event)
        
        return events

