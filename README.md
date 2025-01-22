## eventstarts: Simple python script to check if an event starts in the next n minutes and perform an action

Never miss a meeting again. This simple script (which can be run on a cron job) checks if you have a meeting coming up and sends a reminder to a customizeable webhook. I use it to turn on a smart plug.

Works with Google Calendar or any other calendar provider with ics support.

Instructions:
1. Clone the repo
2. Create a virtualenv and run `pip install -r requirements.txt` in it.
3. Edit the values in `main.py`
4. Run `python main.py`

### (optional) Configuring the crontab
I use cron to run this every 20 and 50th minute, to check if any meeting starts 15 minutes from now and turn on a light for 15 minutes if it does. Here's an example crontab (run `crontab -e` to edit):
```crontab
## Check if I have any meetings                                                      
20 * * * * python3 [path_to_main.py]
50 * * * * python3 [path_to_main.py]
```
Replace `[path_to_main.py]` with the full path of your [main.py](main.py) file.
