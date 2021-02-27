import os
import random
from slack_bolt import App
from slack_sdk import WebClient, logging
from slack_sdk.errors import SlackApiError
import json
import schedule, time
from MrPeanutButter.db_utils import DataBaseUtils

##################################
#### General Helper Functions ####
##################################

def schedule_helper(int_weekday, int_freq, str_time, action, **kwargs):
    """
    Helper function to schedule recurring jobs.

    :param int_weekday: int (1-7), 1-Monday, 2-Tuesday...7-Sunday
    :param int_freq: int, int, 1-every week, 2-every other week...
    :param str_time: int, 24hour format e.g. "16:30"
    :param sec_sleep: int, int, how often that the system should look for pending jobs
    :return: None
    """
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

##################################
#### Create RandomGroup Class ####
##################################
class RandomGroups:  
    """
    This class will focus on initiate group chats for users who agree to join the event
    """
    def __init__(self, bot_token, chat_prompts, group_size, channel_name="mban"):
        """
        Take a list of users and generate random groups at a specified time.

        :param active_user_ids: a list of users who will join the random group event
        :param group_size: pre-defined group size
        """
        self.bot_token = bot_token
        self.chat_prompts = chat_prompts
        self.group_size = group_size
        self.channel_name = channel_name
        self.logger = logging.getLogger("mr.pb.logger")

    def _generate_groups(self, lst, n):
        """
        Helper function to generate groups of n from the lst.

        :param lst: a list
        :param n: the size of the group
        :return: a list of groups
        """
        for i in range(0, len(lst), n):
            yield lst[i:i+n]

    def _assign_random_groups(self, user_ids):
        """
        Assign list of users to random groups.
        
        :param user_ids: list, list of user ids to split into random groups
        :return lst_groups: list of groups of users
        """
        num_users = len(user_ids)
        mod = num_users % self.group_size
        random.shuffle(user_ids)

        # safe guard against the case that only a few people want to join the group
        if num_users == 1:
            return None

        # if the group size is 2 and number of participants is odd, add one user to a random group
        if self.group_size==2:
            if mod == 1:
                single_user = user_ids.pop(0)
                lst_groups = list(self._generate_groups(user_ids, self.group_size))
                lst_groups[0].insert(0, single_user)
                return lst_groups
            else:
                lst_groups = list(self._generate_groups(user_ids, self.group_size))
                return lst_groups

        # if the group size is more than 2,
        # make sure the number of members in a group is no more than group_size; and
        # minimum 2 members in a group
        # e.g. group_size = 4, and we have 4, 4, 1 --> groups will be 4, 2, 3. In other words, group 5 is not allowed.
        if self.group_size > 2:
            if mod > 1:
                smaller_group = user_ids[0:mod]
                lst_groups = list(self._generate_groups(user_ids[mod:], self.group_size))
                lst_groups.append(smaller_group)
                return lst_groups
            if mod == 1:
                temp = user_ids[0:self.group_size+1]
                lst_groups = list(self._generate_groups(user_ids[self.group_size+1:], self.group_size))
                lst_groups = lst_groups + [temp[:len(temp)//2], temp[:len(temp)//2:]]
                return lst_groups
            if mod ==0:
                return list(self._generate_groups(user_ids, self.group_size))

    def start_group_chats(self):
        """
        Groups all participating people randomly and start group chats. Called by schedule_group_chats()
        """
        db = DataBaseUtils(channel_name=self.channel_name)
        users_in_person = db.get_users(participate=True, virtual=False)
        users_virtual = db.get_users(participate=True, virtual=True)

        random.seed(round(time.time()) % 1e5 ) ## put random seed to make sure we don't get the same groups everytime
        random_groups_in_person = self._assign_random_groups(users_in_person)
        random_groups_virtual = self._assign_random_groups(users_virtual)

        # random_groups = random_groups_in_person + random_groups_virtual

        client = WebClient(token=os.environ.get(self.bot_token))

        # initialize chats for each random group
        for group in random_groups_in_person:
            try:
                result = client.conversations_open(
                    token=self.bot_token,
                    users=','.join(group))

                #TODO: edit the message to look better
                client.chat_postMessage(
                    token=self.bot_token,
                    channel=result['channel']['id'],
                    text="Ta daa! \nDesinty created this group. Everyone here is up for IN-PERSON meetup. "+\
                         "Consider using <https://www.when2meet.com|when2meet> to schedule a time.\n"+\
                         "Now, answer the following question: \n\n" +
                         random.sample(self.chat_prompts['responses'], 1)[0])

            except SlackApiError as e:
                self.logger.error(f"Error scheduling message for users {group}: {e}")

        self.logger.info("finieshed creating in person random groups")

        for group in random_groups_virtual:
            try:
                result = client.conversations_open(
                    token=self.bot_token,
                    users=','.join(group))

                #TODO: edit the message to look better
                client.chat_postMessage(
                    token=self.bot_token,
                    channel=result['channel']['id'],
                    text="Ta daa! \nDesinty created this group. Everyone here is up for VIRTUAL meetup. "+\
                         "Consider using <https://www.when2meet.com|when2meet> to schedule a time.\n"+\
                         "Now, answer the following question: \n\n" +
                         random.sample(self.chat_prompts['responses'], 1)[0])

            except SlackApiError as e:
                self.logger.error(f"Error scheduling message for users {group}: {e}")

        self.logger.info("finieshed creating virtual random groups")

    def schedule_group_chats(self, int_weekday, int_freq, str_time, sec_sleep):
        """ Schedule group chats every week using given parameters.

        :param int_weekday: int (1-7), 1-Monday, 2-Tuesday...7-Sunday
        :param int_freq: int, 1-every week, 2-every other week...
        :param str_time: str, 24hour format e.g. "16:30"
        :param sec_sleep: int, how often that the system should look for pending jobs
        :return: None
        """
        schedule_helper(int_weekday, int_freq, str_time, self.start_group_chats)

        while True:
            # Checks whether a scheduled task is pending to run or not
            schedule.run_pending()
            time.sleep(sec_sleep)


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
        Take a user and ask them if they would like to participate in this week's RandomGroup and virtually or not.

        :param bot_token: a string, bot token
        :param user_ids: a list, that contains all user ids in the channel
        :param channel_name: a string, channel name e.g. "mban2021", no space or any special characters
        """
        self.user_ids = user_ids
        self.bot_token = bot_token
        self.channel_name = channel_name
        self.logger = logging.getLogger("mr.pb.logger")

    def send_message(self, user_id):
        """
        Ask a user whether he/she would like to participate in the upcoming round of random group.

        :param user_id: a string that represents a user id
        :return: None
        """
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
            self.logger.error(f"Error scheduling message for user {user_id}: {e}")
        
    def send_message_to_all(self):
        """
        Send participation inquiry message to all users in the channel.

        :return: None
        """
        DataBaseUtils(self.channel_name).refresh_participation()

        ## send message to every user
        for user_id in self.user_ids:
            self.send_message(user_id)
        
        self.logger.info("sent participation messages to all")

    def schedule_messages(self, int_weekday, int_freq, str_time, sec_sleep):
        """
        Schedule to send the participation message to all users in the channel.

        See documentation for schedule_helper function.
        """
        schedule_helper(int_weekday, int_freq, str_time, self.send_message_to_all)

        while True:
            # Checks whether a scheduled task is pending to run or not
            schedule.run_pending()
            time.sleep(sec_sleep)


###################################
#### Pick a Random Quote       ####
###################################
def pick_random_quote(path='responses/class_quotes.json'):
    """
    Get a random quote from a jason file.
    
    :param path: a string that indicates the location where the quotes are stored.
    :return: a random quote
    """
    with open(path) as f:
        responses = json.loads(f.read())
    random.seed(round(time.time()) % 1e5) ## put random seed to make sure we don't get the same groups everytime
    response = random.sample(responses['responses'], 1)[0]
    return '"' + response["quote"] + '"' + " -- " + response["quotee"]