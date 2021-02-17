import os
import random
from slack_bolt import App
from slack_sdk import WebClient, logging
from slack_sdk.errors import SlackApiError
import json
import schedule, time
from db_utils import DataBaseUtils 


##################################
#### Create RandomGroup Class ####
##################################
class RandomGroups:  
    """
    This class will focus on initiate group chats for users who agree to join the event
    """
    def __init__(self, bot_token, user_ids, group_size):
        """
        Take a list of users and generate random groups at a specified time

        :param active_user_ids: a list of users who will join the random group event
        :param group_size: pre-defined group size
        """
        self.bot_token = bot_token
        self.user_ids = user_ids
        self.group_size = group_size
        self.random_groups = self._assign_random_groups()

    # helper function
    def _generate_groups(self, lst, n):
        """Generate groups of n from the lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i+n]

    # main function
    def _assign_random_groups(self):
        num_users = len(self.user_ids)
        mod = num_users % self.group_size
        random.shuffle(self.user_ids)

        # if the group size is 2 and number of participants is odd, add one user to a random group
        if self.group_size==2:
            if mod == 1:
                single_user = self.user_ids.pop(0)
                lst_groups = list(self._generate_groups(self.user_ids, self.group_size))
                lst_groups[0].insert(0, single_user)
                return lst_groups
            else:
                lst_groups = list(self._generate_groups(self.user_ids, self.group_size))
                return lst_groups

        # if the group size is more than 2,
        # make sure the number of members in a group is no more than group_size; and
        # minimum 2 members in a group
        # e.g. group_size = 4, and we have 4, 4, 1 --> groups will be 4, 2, 3. In other words, group 5 is not allowed.
        if self.group_size > 2:
            if mod > 1:
                smaller_group = self.user_ids[0:mod]
                lst_groups = list(self._generate_groups(self.user_ids[mod:], self.group_size))
                lst_groups.append(smaller_group)
                return lst_groups
            if mod == 1:
                temp = self.user_ids[0:self.group_size+1]
                lst_groups = list(self._generate_groups(self.user_ids[self.group_size+1:], self.group_size))
                lst_groups = lst_groups + [temp[:len(temp)//2], temp[:len(temp)//2:]]
                return lst_groups
            if mod ==0:
                return list(self._generate_groups(self.user_ids, self.group_size))

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
            # Checks whether a scheduled task is pending to run or not
            schedule.run_pending()
            time.sleep(sec_sleep)

## Helper function to schedule messages
def schedule_helper(int_weekday, int_freq, str_time, action, **kwargs):
    if int_weekday == 1:
        schedule.every(int_freq).monday.at(str_time).do(action, **kwargs)
    if int_weekday == 2:
        schedule.every(int_freq).tuesday.at(str_time).do(action, **kwargs)
    if int_weekday == 3:
        schedule.every(int_freq).wednesday.at(str_time).do(action, **kwargs)
    if int_weekday == 4:
        schedule.every(int_freq).thursday.at(str_time).do(action, **kwargs)
    if int_weekday == 5:
        schedule.every(int_freq).friday.at(str_time).do(action, **kwargs)
    if int_weekday == 6:
        schedule.every(int_freq).saturday.at(str_time).do(action, **kwargs)
    if int_weekday == 7:
        schedule.every(int_freq).sunday.at(str_time).do(action, **kwargs)

    return None


###############################################
#### Create RandomGroupParticipation Class ####
###############################################

class RandomGroupParticipation:

    """
    This class will focus on asking users whether they want to signup for the random group
    """
    def __init__(self, 
                bot_token: str, 
                user_ids: list, 
                channel_name: str):
        """
        Take a user and ask them if they would like to participate in
        this week's RandomGroup and virtually or not
        """
        self.user_ids = user_ids
        self.bot_token = bot_token
        self.channel_name = channel_name

    def send_message(self, user_id):

        logger = logging.getLogger()
        client = WebClient(token=os.environ.get(self.bot_token))

        try:
            result = client.conversations_open(
                token=self.bot_token,
                users=user_id)
            with open('responses/rg_participation_message.json') as f:
                js_message = json.loads(f.read())
            # interactive message asking if they will participate
            client.chat_postMessage(
                token=self.bot_token,
                channel=result['channel']['id'],
                text="Would you like to participate in this week's random groups?",
                blocks=js_message)

        except SlackApiError as e:
            logger.error("Error scheduling message: {}".format(e))
        
    def send_message_to_all(self):
        DataBaseUtils(self.channel_name).refresh_participation()

        ## send message to every user
        for user_id in self.user_ids:
            self.send_message(user_id)

    def schedule_messages(self, int_weekday, int_freq, str_time, sec_sleep):
        schedule_helper(int_weekday, int_freq, str_time, self.send_message_to_all)

        while True:
            # Checks whether a scheduled task is pending to run or not
            schedule.run_pending()
            time.sleep(sec_sleep)


###################################
#### Pick a Random Quote       ####
###################################
def pick_random_quote(path='responses/class_quotes.json'):
    with open(path) as f:
        responses = json.loads(f.read())
    response = random.sample(responses['responses'], 1)
    return((response["quote"], response["quotee"]))