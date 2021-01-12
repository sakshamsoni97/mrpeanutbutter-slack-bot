import os
import json
import random
from slack_bolt import App

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Send DB's quotes
with open('./db_quotes.json') as f:
    db_quotes = json.loads(f.read())

@app.message("db")
def quote_DB(say):
    say(random.sample(db_quotes['responses'], 1)[0])

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))