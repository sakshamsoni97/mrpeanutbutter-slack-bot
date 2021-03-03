import os
from slack_bolt import App
from slack_sdk import WebClient, logging
from slack_sdk.errors import SlackApiError
from utils import *
import psycopg2
import pandas


"""
WARNING
=======

Script adds rows to tables. Run only when needed to update database.

"""

def create_users_table(channel_name, channel_id, DATABASE_URL):
    ## read all user_ids
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    client = WebClient(token=bot_token)
    response = client.conversations_members(channel=channel_id)
    user_ids = response["members"][1:]

    # connect to database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    ## create table
    cur.execute(f"CREATE TABLE if not exists users_{channel_name} (user_id VARCHAR(20) PRIMARY KEY, participate INTEGER, virtual INTEGER)")

    ## insert each user into the table
    for user_id in user_ids:
        cur.execute(f"INSERT INTO users_{channel_name}(user_id, participate, virtual) VALUES (\'{user_id}\', 0, 0)")

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    DATABASE_URL = os.environ.get("DATABASE_URL")
    create_users_table("mban", "G01QENN3G65", DATABASE_URL)