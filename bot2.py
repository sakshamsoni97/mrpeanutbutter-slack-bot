import os
from slack_bolt import App

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

@app.message(":wave:")
def say_hello(message, say):
    user = message['user']
    say(f"Hi there, <@{user}>!")

@app.message("knock knock")
def ask_who(message, say):
    say("_Who's there?_")

def main():
    app.start(port=int(os.environ.get("PORT", 3000)))
    return

# Start your app
if __name__ == "__main__":
    main()
