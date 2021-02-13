import os
import re
import datetime
from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient, logging
import sqlite3

from MrPeanutButter.bot_utils import RandomGroups

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# today = datetime.date.today()
# scheduled_time = datetime.time(hour=11, minute=6)
# schedule_timestamp = datetime.datetime.combine(today, scheduled_time).strftime('%s')
# logger = logging.getLogger()
# client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
# try:
#   # Call the chat.scheduleMessage method using the WebClient
#   result = client.chat_scheduleMessage(
#       channel="G01HD2W1CVA",
#       text="Ta daa! \nThis was a Scheduled message at 11:06",
#       post_at=schedule_timestamp
#   )
#   # Log the result
#   logger.info(result)
# except SlackApiError as e:
#     logger.error("Error scheduling message: {}".format(e))

# connection = sqlite3.connect(":memory:")
# cursor = connection.cursor()
# sql_file = open("Untitled.sql")
# sql_as_string = sql_file.read()
# print(sql_as_string)
# cursor.executescript(sql_as_string)

# for user in cursor.execute("SELECT user FROM users"):
#   print(user)

@app.message("Test: check current users")
def add_user(message, say):
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()
    sql_file = open("Untitled.sql")
    sql_as_string = sql_file.read()
    cursor.executescript(sql_as_string)

    for user in cursor.execute("SELECT user FROM users"):
      say(user)

@app.message("rg")
def post_random_groups(message):
    # do something
    return

@app.message(":wave:")
def say_hello(message, say):
    user = message['user']
    say(f"Hi there, <@{user}>!")

@app.message("knock knock")
def ask_who(message, say):
    say("_Who's there?_")

@app.message("schedule")
def schedule_message(client, event, logger):
  today = datetime.date.today()
  scheduled_time = datetime.time(hour=11, minute=6)
  schedule_timestamp = datetime.datetime.combine(today, scheduled_time).strftime('%s')

  # Create a timestamp for tomorrow at 9AM
  # now = datetime.datetime.now()
  # future = now + datetime.timedelta(0,60)
  # schedule_timestamp = future.strftime('%s')
  try:
    # Call the chat.scheduleMessage method using the WebClient
    result = client.chat_scheduleMessage(
        channel="G01HD2W1CVA",
        text="Ta daa! \nThis was a Scheduled message at 11:06",
        post_at=schedule_timestamp
    )
    # Log the result
    logger.info(result)
  except SlackApiError as e:
      logger.error("Error scheduling message: {}".format(e))

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Welcome to your _App's Home_* :tada:"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
            }
          },
          {
            "type": "actions",
            "elements": [
              {
                "type": "button",
                "text": {
                  "type": "plain_text",
                  "text": "Click me!"
                }
              }
            ]
          }
        ]
      }
    )

  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
