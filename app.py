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
with open('responses/chat_prompts.json') as f:
   chat_prompts = json.loads(f.read())

# Initializes the app
app = App(
  token=SLACK_BOT_TOKEN,
  signing_secret=SLACK_SIGNING_SECRET
)

# logger
if not os.path.exists("logs/"):
  os.mkdir("logs/")

logger_filename = "logs/MrPB_runtime_logs.log"
logging.basicConfig(
      filename=logger_filename,
      level=logging.DEBUG,
      format="%(asctime)s | %(module)s | %(levelname)s | %(message)s",
      datefmt="%m-%d-%Y %I:%M:%S %p",
  )
logger = logging.getLogger("mr.pb.logger")

### Random Quote ###

@app.command("/quote")
def send_random_quote(ack, say, command):
  ack()
  say(pick_random_quote())


### Weekly Participation Messages ###

# user initiated participation update
@app.action("update-participation")
def send_participation_message(ack, say, body):
  ack()
  user = body["user"]["id"]
  RandomGroupParticipation(bot_token=SLACK_BOT_TOKEN, user_ids=[], channel_name="mban").send_message(user)

# check participation status
@app.action("participation-status")
def check_participation_status(ack, say, body):
  ack()
  user = body["user"]["id"]
  say("Whoops... looks like I don't have this capability right now. In other words, someone was too lazy to code this.")


# get the response
@app.action("rg-in-person")
def get_inperson_participant(ack, say, body):
  ack()
  say('Great! You are confirmed for an IN-PERSON random meetup.')
  logger.info(f"{body['user']['username']} responded {body['actions'][0]['action_id']}")  # TODO: change this to logging in file
  DataBaseUtils(channel_name="mban").\
    update_user_response(user_id=body['user']['id'], participating=True, virtual=False)

@app.action("rg-virtual")
def get_virtual_participant(ack, say, body):
  ack()
  say('Great! You are confirmed for a VIRTUAL random meetup.')
  logger.info(f"{body['user']['username']} responded {body['actions'][0]['action_id']}")
  DataBaseUtils(channel_name="mban").\
    update_user_response(user_id=body['user']['id'], participating=True, virtual=True)

@app.action("rg-no")
def get_not_participating(ack, say, body):
  ack()
  say('Oh no! We are sad that you cannot make it this time, please consider joining the next one!')
  logger.info(f"{body['user']['username']} responded {body['actions'][0]['action_id']}")
  DataBaseUtils(channel_name="mban").\
    update_user_response(user_id=body['user']['id'], participating=False, virtual=False)


### Random Groups ###

@app.event("app_mention")
def respond_to_mention(ack, say, body):
  ack()
  message = body['event']['text']
  if ':wave:' in message:
    say(f"Hello, <@{body['event']['user']}>")
  elif 'knock knock' in message:
    say("Woof! who's there?")
  else:
    say("Sorry, I didn't get that one")


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  user = event["user"]
  try:
    client.views_publish(
      user_id=user,
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

### Start the app ###
if __name__ == "__main__":
  user_ids = DataBaseUtils(channel_name="mban").get_users()

  ## schedule weekly participation messages
  RandomGroupParticipation(bot_token=SLACK_BOT_TOKEN, user_ids=user_ids, channel_name="mban").\
    schedule_messages(int_weekday=1, int_freq=1, str_time='16:29', sec_sleep=10)

  ## schedule random group
  RandomGroups(bot_token=SLACK_BOT_TOKEN, chat_prompts=chat_prompts, group_size=2).\
    schedule_group_chats(int_weekday=2, int_freq=1, str_time='16:29', sec_sleep=10)

  app.start(port=int(os.environ.get("PORT", 3000)))