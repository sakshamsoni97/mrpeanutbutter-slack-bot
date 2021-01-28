import os
import json
import random
from slack_bolt import App

# Initializes your app with your bot token and signing secret

###################################
#### Create Random Quote Class ####
###################################

class RandomQuote:
    def __init__(self, quotes):
        self.quotes = quotes

    def generate_a_quote(self):
        return(random.sample(self.quotes['responses'], 1)[0])

###########################
#### Generate Quotes ######
###########################
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

@app.message("db")
def quote_DB(say):
    with open('./db_quotes.json') as f:
        db_quotes = json.loads(f.read())
    say(RandomQuote(db_quotes).generate_a_quote())

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))