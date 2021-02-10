import os
from slack_bolt import App, Respond, Ack
from slack_sdk import WebClient, logging
from slack_sdk.errors import SlackApiError
import json
from utils import *

with open('./rg_participation_message.json') as f:
    js_message = json.loads(f.read())

###############################################
#### Create RandomGroupParticipation Class ####
###############################################

class RandomGroupParticipation:

    """
    This class will focus on asking users whether they want to signup for the random group
    """
    def __init__(self, bot_token, user_id):
        """
        Take a user and ask them if they would like to participate in
        this week's RandomGroup and virtually or not
        """
        self.user_id = user_id
        self.bot_token = bot_token

    # to send interactive message to users
    # TODO: Make this weekly and update the SQL weekly to set everything to 0
    def send_message(self):

        logger = logging.getLogger()
        client = WebClient(token=os.environ.get(self.bot_token))

        try:
            result = client.conversations_open(
                token=self.bot_token,
                users=self.user_id)

            # interactive message asking if they will participate
            client.chat_postMessage(
                token=self.bot_token,
                channel=result['channel']['id'],
                text="Would you like to participate in this week's random groups?",
                blocks=js_message)

        except SlackApiError as e:
            logger.error("Error scheduling message: {}".format(e))

#######################
#### Setup the Env ####
#######################
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

#TODO: create a class that generate a list of active users & post messages at a pre-specified time
bot_token = 'TBD'
user_ids = ['W015KRJ3L4C', 'W0156U3CTEJ']

# send message questions
for user in user_ids:
    RandomGroupParticipation(bot_token=bot_token, user_id=user).send_message()
    #TODO: @Saksham, when integrating the pipeline, this script will need to be scheduled to run on e.g. weekly basis
    # FYI, you could leverage the helper in utils.py, but you might have a better way of doing it

# get the response
@app.action("rg-in-person")
def get_participation(ack, say, body):
    ack()
    say('Great! You are confirmed for an IN-PERSON random meetup.')
    # body has all the info that you could possibly need for that user action
    print(body['user']['username'], body['actions'][0]['value'])
    #TODO: @Saksham & @Daniel - add a function in the line below to update your user status! - let us know if u have questions

@app.action("rg-virtual")
def get_participation(ack, say, body):
    ack()
    say('Great! You are confirmed for a VIRTUAL random meetup.')
    print(body['user']['username'], body['actions'][0]['value'])

@app.action("rg-no")
def get_participation(ack, say, body):
    ack()
    say('Oh no! We are sad that you cannot make it this time, please consider joining the next one!')
    print(body['user']['username'], body['actions'][0]['value'])

if __name__ == "__main__":
   app.start(port=int(os.environ.get("PORT", 3000)))
