import os
from utils import *
import psycopg2
import pandas



###################################
####   DataBase interface      ####
###################################
class DataBaseUtils():
    def __init__(self, channel_name: str):
        # self.DATABASE_URL = "postgres://ntdoljutfrviin:52ca35af72485747db891c09ccc53575995eff89c370e6d2b2d07f2655dd177d@ec2-54-90-13-87.compute-1.amazonaws.com:5432/d7u9v3u0shgd1c"
        self.DATABASE_URL = os.environ["DATABASE_URL"]
        self.channel_name = channel_name

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
        cur.execute(f"UPDATE users_{self.channel_name} SET participate = {participating}, virtual = {virtual} WHERE user_id = {user_id}")

        conn.commit()
        cur.close()
        conn.close()

    def refresh_table(self):
        """
        Update user list
        """

