import requests, pytz, recurring_ical_events
from datetime import datetime, timedelta, time
from icalendar import Calendar, vCalAddress

def _is_going(username: str, participants: list[vCalAddress] | vCalAddress | None) -> bool:
  return _rsvp(username, participants) in (None, 'ACCEPTED')

def _rsvp(username: str, participants: list[vCalAddress] | vCalAddress | None) -> str | None:
  """Returns username's PARTSTAT (ACCEPTED, TENTATIVE, NEEDS-ACTION, DECLINED), or None if
  the event has no attendees. icalendar returns a single attendee unwrapped."""
  if participants is None:
    return None
  if not isinstance(participants, list):
    participants = [participants]
  for participant in participants:
    if username in participant.params.get('CN', ''):
      return participant.params.get('PARTSTAT', 'NEEDS-ACTION')
  return 'NOT-INVITED'

def todays_events(url: str, timezone: str, username: str|None = None) -> list[dict]:
  """
  This function lists today's events in an ICS url, including ones already over.

  Args:
      url (str): URL to the ICS file.
      timezone (str): Time zone that defines "today", e.g. "America/Los_Angeles".
      username (str): Name of attendee whose declined events are left out.

  Returns:
      list[dict]: {"summary", "start", "end", "rsvp"} per event, sorted by start, with ISO 8601
      times in timezone. All-day and cancelled events are skipped.
  """
  zone = pytz.timezone(timezone)
  day_start = zone.localize(datetime.combine(datetime.now(zone).date(), time.min))
  return _timed_events(_calendar(url), zone, day_start, day_start + timedelta(days=1), username)

def first_event_after_today(url: str, timezone: str, username: str|None = None, days: int = 14) -> dict|None:
  """
  This function finds the first event after today in an ICS url, e.g. tomorrow morning's
  first meeting, or Monday's when today is Friday.

  Args:
      url (str): URL to the ICS file.
      timezone (str): Time zone that defines "today", e.g. "America/Los_Angeles".
      username (str): Name of attendee whose declined events are left out.
      days (int): How many days after today to look.

  Returns:
      dict|None: The event, in the same form as todays_events(), or None if there is none.
  """
  zone = pytz.timezone(timezone)
  tomorrow = zone.localize(datetime.combine(datetime.now(zone).date() + timedelta(days=1), time.min))
  events = _timed_events(_calendar(url), zone, tomorrow, tomorrow + timedelta(days=days), username)
  # between() also returns events that started today and are still running at midnight
  return next((e for e in events if datetime.fromisoformat(e["start"]) >= tomorrow), None)

def _calendar(url: str) -> Calendar:
  response = requests.get(url, timeout=30)
  response.raise_for_status()
  return Calendar.from_ical(response.text)

def _timed_events(calendar: Calendar, zone, start: datetime, end: datetime, username: str|None) -> list[dict]:
  """Timed events between start and end (including ones already running at start), sorted, in
  the form todays_events() returns."""
  events = []
  for component in recurring_ical_events.of(calendar).between(start, end):
    if component.name != "VEVENT" or component.get("STATUS") == "CANCELLED":
      continue
    event_start = component.get("DTSTART").dt
    if not isinstance(event_start, datetime):
      continue  # All-day events have a date, not a datetime
    if component.get("DTEND"):
      event_end = component.get("DTEND").dt
    else:
      event_end = event_start + (component.get("DURATION").dt if component.get("DURATION") else timedelta())
    event_start, event_end = (zone.localize(t) if t.tzinfo is None else t.astimezone(zone) for t in (event_start, event_end))

    rsvp = _rsvp(username, component.get("ATTENDEE")) if username else None
    if rsvp in ('DECLINED', 'NOT-INVITED'):
      continue
    events.append({
      "summary": str(component.get("SUMMARY", "Untitled event")),
      "start": event_start.isoformat(),
      "end": event_end.isoformat(),
      "rsvp": (rsvp or 'ACCEPTED').lower(),
    })
  return sorted(events, key=lambda e: e["start"])

def any_meetings_starting(url: str, minutes_from_now: int, username: str|None = None) -> bool:
  """
  This function checks if any events in an ICS url start in the next n minutes.

  Args:
      url (str): URL to the ICS file.
      minutes_from_now (int): How many minutes from now to check.
      username (str): Name of attendee to check if they have RSPV'd yes.

  Returns:
      bool: True if an event starts within minutes_from_now, False otherwise.
  """
  now = pytz.utc.localize(datetime.utcnow())
  print("now", str(now))

  tomorrow = now + timedelta(days=1)
  start_date = (now.year, now.month, now.day)
  end_date = (tomorrow.year, tomorrow.month, tomorrow.day)

  try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for non-200 status codes
    
    # Parse ICS data using icalendar
    calendar = Calendar.from_ical(response.text)
    
    for component in recurring_ical_events.of(calendar).between(start_date, end_date):
      # Look for events (VEVENT)
      if component.name == "VEVENT":
        # Get event start time (consider time zone)
        if component.get("DTSTART"):
          start_time = component.get("DTSTART").dt
        else:
          # Handle missing start time (optional: log or return False)
          continue
        
        # Check if event starts within n minutes
        print(component.get("SUMMARY"))
        n_minutes_from_now = now + timedelta(minutes=minutes_from_now)

        start_time_utc = start_time.astimezone(pytz.utc)
        print("start_time", str(start_time_utc))
        participants = component.get("ATTENDEE")
        rsvp = _is_going(username, participants) if username else True
        print("RSVP:", rsvp)
        
        if start_time_utc >= now and start_time_utc <= n_minutes_from_now and rsvp:
          return True
    
    return False
  except requests.exceptions.RequestException as e:
    print(f"Error fetching ICS file: {e}")
    return False


