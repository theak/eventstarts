# Simple python script to check if an event starts in the next n minutes and perform an action

Never miss a meeting again. This simple script (which can be run on a cron job) checks if you have a meeting coming up and sends a reminder to a customizeable webhook. I use it to turn on a smart plug.

Works with Google Calendar or any other calendar provider with ics support.

## Instructions
1. Clone the repo
2. Create a virtualenv and run `pip install -r requirements.txt` in it.
3. Edit the values in `main.py`
4. Run `python main.py`

## Configuring a crontab (optional)
I use cron to run this every 20 and 50th minute, to check if any meeting starts 30 minutes from now and turn on a light for 15 minutes if it does. Here's an example crontab (run `crontab -e` to edit):
```crontab
## Check if I have any meetings                                                      
20 * * * * python3 [path_to_main.py]
50 * * * * python3 [path_to_main.py]
```
Replace `[path_to_main.py]` with the full path of your [main.py](main.py) file.

## Sending today's meetings somewhere (optional)
[today.py](today.py) POSTs the rest of today's events as JSON, e.g. to a Home Assistant webhook, so a voice assistant can answer "when's my next meeting?". It sends every timed event today that you haven't declined (accepted, tentative or not yet answered), skips all-day events, and converts times to your time zone:
```json
{"events": [{"summary": "Design review", "start": "2026-10-05T14:00:00-07:00", "end": "2026-10-05T14:30:00-07:00", "rsvp": "tentative"}]}
```
Edit the values in `today.py`, then run it every 15 minutes:
```crontab
*/15 * * * * python3 [path_to_today.py]
```
Events that have already ended are included, so the receiver should compare times when it reads them rather than rely on each run being recent.
