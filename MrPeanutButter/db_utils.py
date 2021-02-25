import os
from utils import *
import psycopg2
import pandas as pd



###################################
####   DataBase interface      ####
###################################
class DataBaseUtils():
    def __init__(self, channel_name: str = "mban"):
        self.DATABASE_URL = os.environ["DATABASE_URL"]
        self.channel_name = channel_name

    def get_users(self, participate: bool = None, virtual: bool = False):
        """
        get list of all users in a channel

        :return: list, user_ids
        """
        conn = psycopg2.connect(self.DATABASE_URL, sslmode='require')
        cur = conn.cursor()

        ## refresh participate values
        cur.execute(f"SELECT * FROM users_{self.channel_name}")
        users = pd.DataFrame(cur.fetchall(), columns=['user_id', 'participate', 'virtual'])

        cur.close()
        conn.close()

        if participate is not None:
            users = users.query(f"participate == {int(participate)} and virtual == {int(virtual)}")

        return users.user_id.to_list()
    
    def refresh_participation(self):
        """
        Refresh participate column of the user table
        """
        conn = psycopg2.connect(self.DATABASE_URL, sslmode='require')
        cur = conn.cursor()

        ## refresh participate values
        cur.execute(f"UPDATE users_{self.channel_name} SET participate = 0")

        conn.commit()
        cur.close()
        conn.close()

    def update_user_response(self,
                            user_id: str, 
                            participating: bool, 
                            virtual: bool):
        """
        Update a user's participating and virtual setting based on the response

        :param user_id str
        :param participating bool
        :param virtual bool
        """
        conn = psycopg2.connect(self.DATABASE_URL, sslmode='require')
        cur = conn.cursor()

        ## refresh participate values
        cur.execute(f"UPDATE users_{self.channel_name} SET participate = {int(participating)}, virtual = {int(virtual)} WHERE user_id = {user_id}")

        conn.commit()
        cur.close()
        conn.close()

    def refresh_table(self):
        """
        Update user list
        """
        raise NotImplementedError

