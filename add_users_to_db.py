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

Script overwrites tables. Run only when needed to update database.

"""

## initialize the app
# app = App(
#     token=os.environ.get("SLACK_BOT_TOKEN"),
#     signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
# )

def create_users_table(channel_name, channel_id, DATABASE_URL):
    ## read all user_ids
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    client = WebClient(token=bot_token)
    response = client.conversations_members(channel=channel_id)
    user_ids = response["members"][1:]

    # user_ids = ["111", "222", "333"]

    ## connect to database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    ## create table
    cur.execute("CREATE TABLE users_%s (user_id VARCHAR(20) PRIMARY KEY, participate INTEGER, virtual INTEGER)" %(channel_name,))

    ## insert each user into the table
    for user_id in user_ids:
        cur.execute(f"INSERT INTO users_{channel_name}(user_id, participate, virtual) VALUES ({user_id}, 0, 0)")

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    # app.start(port=int(os.environ.get("PORT", 3000)))
    create_users_table("mban", "G01HD2W1CVA", "postgres://ntdoljutfrviin:52ca35af72485747db891c09ccc53575995eff89c370e6d2b2d07f2655dd177d@ec2-54-90-13-87.compute-1.amazonaws.com:5432/d7u9v3u0shgd1c")
    # exit()