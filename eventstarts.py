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
  day_end = day_start + timedelta(days=1)

  response = requests.get(url, timeout=30)
  response.raise_for_status()
  calendar = Calendar.from_ical(response.text)

  events = []
  for component in recurring_ical_events.of(calendar).between(day_start, day_end):
    if component.name != "VEVENT" or component.get("STATUS") == "CANCELLED":
      continue
    start = component.get("DTSTART").dt
    if not isinstance(start, datetime):
      continue  # All-day events have a date, not a datetime
    if component.get("DTEND"):
      end = component.get("DTEND").dt
    else:
      end = start + (component.get("DURATION").dt if component.get("DURATION") else timedelta())
    start, end = (zone.localize(t) if t.tzinfo is None else t.astimezone(zone) for t in (start, end))

    rsvp = _rsvp(username, component.get("ATTENDEE")) if username else None
    if rsvp in ('DECLINED', 'NOT-INVITED'):
      continue
    events.append({
      "summary": str(component.get("SUMMARY", "Untitled event")),
      "start": start.isoformat(),
      "end": end.isoformat(),
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


