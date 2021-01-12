import os
import random
from slack_bolt import App
from slack_sdk import WebClient

class RandomGroups:
    def __init__(self, user_ids, group_size):
        # TODO: better setup needed
        self.client = WebClient(token="xoxb-353724937235-1597595805425-mlj5KTMB7F9uD7uNDFOXejlA")
        self.response = self.client.conversations_members(channel="G01HD2W1CVA")

        # TODO: user_ids need to be updated with the users who opt in the upcoming random groups
        self.user_ids = self.response["members"][1:]
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

    # TODO: initialize groups and post a message in a pre-specified time
    def start_group_chats(self):
        return("current groups are:" + str(self.random_groups))

#######################
#### Setup the Env ####
#######################
# Initializes the app with the bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

@app.message("rg")
def start_group_chats(say, user_ids=["placeholder here"]):
    say(RandomGroups(user_ids=user_ids, group_size=2).start_group_chats())

if __name__ == "__main__":
   app.start(port=int(os.environ.get("PORT", 3000)))