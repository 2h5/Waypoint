import discord
from discord import app_commands
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
mapbox_token = os.getenv("MAPBOX_TOKEN")


intents = discord.Intents.default()
intents.message_content = True  
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    now = datetime.now()
    timestamp = now.strftime("%b %d, %Y %H:%M%p")
    print(f"Logged in as {client.user} at {timestamp}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

from commands.speed import setup as speed
from commands.sixseven import setup as sixseven
from commands.good import setup as good
from commands.staticmap import setup as staticmap
from commands.route import setup as route
from commands.translate import setup as translate
from commands.remindme import setup as remindme


from commands.usps import setup as usps


speed(tree)
sixseven(tree)
good(tree)
staticmap(tree)
route(tree)
translate(tree)
remindme(tree)
usps(tree)

client.run(discord_token)

