import requests

from eventstarts import todays_events, first_event_after_today

""" ics_url: Replace this with your ical URL (see main.py) """
ics_url: str = "YOUR_ICS_URL_HERE"

""" timezone: Your time zone, which decides when "today" starts and ends """
timezone: str = "America/Los_Angeles"

""" (optional) username: Username whose declined events are left out """
username = None

""" post_url: URL to POST today's events to as {"events": [...]}, e.g. a Home Assistant webhook """
post_url: str = "YOUR_WEBHOOK_URL_HERE"

if __name__ == "__main__":
  events = todays_events(ics_url, timezone, username)
  next_event = first_event_after_today(ics_url, timezone, username)
  requests.post(post_url, json={"events": events, "next": next_event}, timeout=30).raise_for_status()
