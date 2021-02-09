import os
import random
from slack_bolt import App
from slack_sdk import WebClient, logging
from slack_sdk.errors import SlackApiError
import json
from utils import *

##################################
#### Create RandomGroup Class ####
##################################
class RandomGroups:
    """
    This class will focus on initiate group chats for users who agree to join the event
    """
    def __init__(self, bot_token, user_ids, group_size):
        # TODO: better setup needed
        """
        Take a list of users and generate random groups at a specified time

        :param active_user_ids: a list of users who will join the random group event
        :param group_size: pre-defined group size
        """
        self.bot_token = bot_token
        self.user_ids = user_ids
        self.group_size = group_size
        self.random_groups = self.assign_random_groups()

    # helper function
    def generate_groups(self, lst, n):
        """Generate groups of n from the lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i+n]

    # main function
    def assign_random_groups(self):
        num_users = len(self.user_ids)
        mod = num_users % self.group_size
        user_ids = random.shuffle(self.user_ids)

        # if the group size is 2 and number of participants is odd, add one user to a random group
        if self.group_size==2:
            if mod == 1:
                single_user = user_ids.pop(0)
                lst_groups = list(self.generate_groups(self.user_ids, self.group_size))
                lst_groups[0].insert(0, single_user)
                return lst_groups
            else:
                lst_groups = list(self.generate_groups(self.user_ids, self.group_size))
                return lst_groups

        # if the group size is more than 2,
        # make sure the number of members in a group is no more than group_size; and
        # minimum 2 members in a group
        # e.g. group_size = 4, and we have 4, 4, 1 --> groups will be 4, 2, 3. In other words, group 5 is not allowed.
        if self.group_size > 2:
            if mod > 1:
                smaller_group = user_ids[0:mod]
                lst_groups = list(self.generate_groups(self.user_ids[mod:], self.group_size))
                lst_groups.append(smaller_group)
                return lst_groups
            if mod == 1:
                temp = user_ids[0:self.group_size+1]
                lst_groups = list(self.generate_groups(self.user_ids[self.group_size+1:], self.group_size))
                lst_groups = lst_groups + [temp[:len(temp)//2], temp[:len(temp)//2:]]
                return lst_groups
            if mod ==0:
                return list(self.generate_groups(self.user_ids, self.group_size))

    def start_group_chats(self, chat_prompts):

        # initialize chats for each random group
        for group in self.random_groups:

            logger = logging.getLogger()
            client = WebClient(token=os.environ.get(self.bot_token))

            try:
                result = client.conversations_open(
                    token=self.bot_token,
                    users=','.join(group))

                client.chat_postMessage(
                    token=self.bot_token,
                    channel=result['channel']['id'],
                    text="Ta daa! \nDesinty created this group. Now, answer the following question: \n\n" +
                         random.sample(chat_prompts['responses'], 1)[0])

            except SlackApiError as e:
                logger.error("Error scheduling message: {}".format(e))

    def schedule_group_chats(self, int_weekday, int_freq, str_time, sec_sleep, chat_prompts):

        schedule_helper(int_weekday, int_freq, str_time, self.start_group_chats,
                        chat_prompts=chat_prompts)

        while True:
            # Checks whether a scheduled task
            # is pending to run or not
            schedule.run_pending()
            time.sleep(sec_sleep)

#######################
#### Setup the Env ####
#######################
# Initializes the app with the bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# get a list of users who agree to join current random group event
#TODO: create a class that generate a list of active users & post messages at a pre-specified time
#TODO: currently os.environ.get("SLACK_BOT_TOKEN") returns None (for me...)
bot_token = os.environ.get("SLACK_BOT_TOKEN")
client = WebClient(token=bot_token)
response = client.conversations_members(channel="G01HD2W1CVA")
user_ids = response["members"][1:]

# import the chat prompts
#TODO: collect more prompts
with open('./chat_prompts.json') as f:
   chat_prompts = json.loads(f.read())

# initiliaze the groups
RandomGroups(bot_token=bot_token, user_ids=user_ids, group_size=2).\
    schedule_group_chats(int_weekday=2, int_freq=1, str_time='16:29', sec_sleep=10, chat_prompts=chat_prompts)

if __name__ == "__main__":
   app.start(port=int(os.environ.get("PORT", 3000)))
