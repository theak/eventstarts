import requests, pytz, recurring_ical_events
from datetime import datetime, timedelta
from icalendar import Calendar

def any_meetings_starting(url: str, minutes_from_now: int) -> bool:
  """
  This function checks if any events in an ICS url start in the next n minutes.

  Args:
      url (str): URL to the ICS file.
      minutes_from_now (int): How many minutes from now to check.

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
        
        if start_time_utc >= now and start_time_utc <= n_minutes_from_now:
          return True
    
    return False
  except requests.exceptions.RequestException as e:
    print(f"Error fetching ICS file: {e}")
    return False


