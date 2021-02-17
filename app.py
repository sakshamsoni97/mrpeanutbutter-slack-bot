import os
import re
import datetime
import logging
import json

from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient, logging

from MrPeanutButter.bot_utils import RandomGroups, RandomGroupParticipation, pick_random_quote
from MrPeanutButter.db_utils import DataBaseUtils

### Initial Set up ###

# Constants
today = datetime.date.today()
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")

# Initializes the app
app = App(
  token=SLACK_BOT_TOKEN,
  signing_secret=SLACK_SIGNING_SECRET
)

### Random Quote ###

@app.command("/quote")
def send_random_quote(ack, say, command):
  ack()
  say(pick_random_quote())


### Weekly Participation Messages ###

# send message questions
# for user in user_ids:
#     RandomGroupParticipation(bot_token=SLACK_BOT_TOKEN, user_ids=users).send_message()

# user initiated participation update
@app.action("update-participation")
def send_participation_message(ack, say, body):
  ack()
  user = body["user"]["user_id"]
  RandomGroupParticipation(bot_token=SLACK_BOT_TOKEN, user_ids=[], channel_name="mban").send_message(user)

# check participation status
@app.action("participation-status")
def check_participation_status(ack, say, body):
  ack()
  user = body["user"]["user_id"]
  say("Whoops... looks like I don't have this capability right now. In other words, someone was too lazy to code this.")


# get the response
@app.action("rg-in-person")
def get_inperson_participant(ack, say, body):
  ack()
  say('Great! You are confirmed for an IN-PERSON random meetup.')
  # body has all the info that you could possibly need for that user action
  print(body['user']['username'], body['actions'][0]['value'])
  #TODO: @Saksham & @Daniel - add a function in the line below to update your user status! - let us know if u have questions

@app.action("rg-virtual")
def get_virtual_participant(ack, say, body):
  ack()
  say('Great! You are confirmed for a VIRTUAL random meetup.')
  print(body['user']['username'], body['actions'][0]['value'])

@app.action("rg-no")
def get_not_participating(ack, say, body):
  ack()
  say('Oh no! We are sad that you cannot make it this time, please consider joining the next one!')
  print(body['user']['username'], body['actions'][0]['value'])


### Random Groups Start ###
with open('responses/chat_prompts.json') as f:
  chat_prompts = json.loads(f.read())

RandomGroups(bot_token=SLACK_BOT_TOKEN, user_ids=user_ids, group_size=2).\
  schedule_group_chats(int_weekday=2, int_freq=1, str_time='16:29', sec_sleep=10, chat_prompts=chat_prompts)

# @app.message("Test: check current users")
# def add_user(message, say):
#     connection = sqlite3.connect(":memory:")
#     cursor = connection.cursor()
#     sql_file = open("Untitled.sql")
#     sql_as_string = sql_file.read()
#     cursor.executescript(sql_as_string)

#     for user in cursor.execute("SELECT user FROM users"):
#       say(user)

# @app.message("rg")
# def post_random_groups(message):
#     # do something
#     return

@app.message(":wave:")
def say_hello(message, say):
  user = message['user']
  say(f"Hi there, <@{user}>!")

@app.message("knock knock")
def ask_who(message, say):
  say("_Who's there?_")


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  user = event["user"]
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=user,
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
              "text": f"OH MY GOD <@{user}> and Mr. Peanuet Butter in the same chat! Is this a cross-over episode?"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "How can I be of service today?"
            }
          },
          {
            "type": "actions",
            "elements": [
              {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Update my Participation Status for this week"
                },
                "style": "primary",
                "value": "update-participation",
                "action_id": "update-participation"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Show my current participation status"
                },
                "style": "primary",
                "value": "participation-status",
                "action_id": "participation-status"
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
