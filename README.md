## eventstarts: Simple python script to check if an event starts in the next n minutes and perform an action

Never miss a meeting again. This simple script (which can be run on a cron job) checks if you have a meeting coming up and sends a reminder to a customizeable webhook. I use it to turn on a smart plug.

Works with Google Calendar or any other calendar provider with ics support.

Instructions:
1. Clone the repo
2. Create a virtualenv and run `pip install -r requirements.txt` in it.
3. Edit the values in `main.py`
4. Run `python main.py`
