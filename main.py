from datetime import datetime
from icalendar import Calendar, Event, vDDDTypes
import requests
import os
from slack_sdk.webhook.client import WebhookClient
from typing import List

def get_calendar() -> Calendar:
    resp = requests.get(os.environ['CALENDAR_URL'])
    resp.raise_for_status()

    return Calendar.from_ical(resp.text)

def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    return dt1.month == dt2.month and dt1.day == dt2.day

def find_birthday_students(cal: Calendar) -> List[str]:
    today = datetime.today()
    students = []

    for vevent in cal.walk('VEVENT'):
        vevent: Event = vevent

        student_name = vevent.get('SUMMARY')
        dtstart: vDDDTypes = vevent.get('DTSTART')
        if isinstance(dtstart.dt, datetime):
            dt = dtstart.dt
            if is_same_day(dt, today):
                students.append(student_name)

    return students

def run(event, context):
    cal = get_calendar()
    students = find_birthday_students(cal)
    if not students:
        return

    if students:
        text = f':tada:今日は {" と ".join(students)} の誕生日です:tada:'
    else:
        text = '今日が誕生日の生徒はいません'

    body = {
        'text': text,
        'icon_emoji': ':shiroko2:',
    }
    webhook_client = WebhookClient(os.environ['SLACK_WEBHOOK_URL'])
    webhook_client.send_dict(body=body)
    print('OK')

if __name__ == '__main__':
    run(None, None)
