import requests

from eventstarts import any_meetings_starting

""" ics_url: Replace this with your ical URL
    For Google Calendar:
    Settings -> Settings for my calendars -> Calendar settings ->
        Secret address in iCal format
"""
ics_url: str = "YOUR_ICS_URL_HERE"

""" minutes_from_now: How many minutes from now to check for events """
minutes_from_now: int = 30

""" (optional) username: Username to check whether or not they have RSVP'd """
username = None

""" (optional) post_url: URL to make a POST request to if an event is starting soon """
post_url: str|None = None

if __name__ == "__main__":
  if any_meetings_starting(ics_url, minutes_from_now, username):
    print("An event starts in the next", minutes_from_now, "minutes!")
    if post_url: requests.post(post_url)
  else:
    print("No events starting in the next", minutes_from_now, "minutes.")
      
        
