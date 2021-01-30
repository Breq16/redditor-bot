import os
import requests

from flask import Flask, redirect
from flask_discord_interactions import DiscordInteractions, InteractionResponse


app = Flask(__name__)
discord = DiscordInteractions(app)


app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


def make_reddit_command(endpoint, info):
    if len(endpoint) < 3:
        name = endpoint + "_"*(3-len(endpoint))
    else:
        name = endpoint

    @discord.command(name=name, description=info["desc"])
    def _reddit_command(ctx):
        result = requests.get(
            f"https://redditor.breq.dev/{endpoint}",
            params={"channel": f"breqbot:{ctx.channel_id}"}).json()
        return InteractionResponse(embed={
            "title": result["title"],
            "url": result["url"],
            "image": {"url": result["url"]}
        })


reddit_endpoints = requests.get("https://redditor.breq.dev/list").json()

for endpoint, info in reddit_endpoints.items():
    make_reddit_command(endpoint, info)

discord.set_route("/interactions")


@app.route("/")
def index():
    return redirect(os.environ["OAUTH_URL"])


discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])
discord.update_slash_commands()


if __name__ == '__main__':
    app.run()
