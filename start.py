import discord
from discord import app_commands
from deep_translator import GoogleTranslator
from datetime import datetime
import os
import re
import io
import asyncio
import aiohttp  
import urllib.parse
from dotenv import load_dotenv

#hiding secrets
load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
mapbox_token = os.getenv("MAPBOX_TOKEN")


intents = discord.Intents.default()
intents.message_content = True  #lets bot read text
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

# translate code
@tree.command(name="translate", description="Translate into a diff lang")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def translate(interaction: discord.Interaction, lang: str, *, text: str):
    """
    Example:
    /translate lang: es text: hello
    """
    now = datetime.now().strftime("%b %d, %Y %H:%M%p")
    user = interaction.user
    username = user.name
    
    try:
        translated = GoogleTranslator(source="auto", target=lang).translate(text)
        await interaction.response.send_message(translated)
        
        print(f"[{now}] ✅ {username} translated to '{lang}' | text: '{text}'")
        
    except Exception as e:
        await interaction.response.send_message(
            "Error, check your language code (ISO 639, 2 character language code required. Case sensitive.)."
        )
        print(f"[{now}] ❌ {username} tried lang='{lang}'")
#uploads 6 7 ¬‿¬
@tree.command(name="sixseven", description = "6 7 uploader")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def image_six_seven(interaction: discord.Interaction):
    folder = "images"
    path = os.path.join(folder, "IMG_1425.png")
   
    with open(path, "rb") as f:
        picture = discord.File(f)
        await interaction.response.send_message(file=picture)
#uploads speed laugh
@tree.command(name="speed", description = "yoo")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def image_speed(interaction: discord.Interaction):
    folder = "images"
    path = os.path.join(folder, "image8.jpg")
   
    with open(path, "rb") as f:
        picture = discord.File(f)
        await interaction.response.send_message(file=picture)
#uploads this guy
@tree.command(name="good", description = "ez")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def image_good(interaction: discord.Interaction):
    folder = "images"
    path = os.path.join(folder, "good.jpg")
   
    with open(path, "rb") as f:
        picture = discord.File(f)
        await interaction.response.send_message(file=picture)
# remind me code
@tree.command(name="remindme", description="Set a reminder for yourself")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def remindme(interaction: discord.Interaction, time: str, *, text: str):
    """
    Example:
    /remindme time: 10m text: take out the trash
    Supported units: s (seconds), m (minutes), h (hours)
    """
    match = re.match(r"^(\d+)([smh])$", time.lower())
    if not match:
        await interaction.response.send_message("Use format like `10m`, `2h`, or `30s`.")
        return

    value, unit = match.groups()
    value = int(value)
    seconds = value * {"s": 1, "m": 60, "h": 3600}[unit]

    await interaction.response.send_message(
        f"{interaction.user.mention}, I'll remind you in {value}{unit}."
    )

    await asyncio.sleep(seconds)

    try:
        await interaction.user.send(f"⏰ Reminder: {text}")
    except discord.Forbidden:
        await interaction.followup.send(f"⏰ Reminder for {interaction.user.mention}: {text}")
        

#add link to url functionality on pause, this was a qrcode converter 



#geocode takes in location and this specific function returns the whole JSON
async def geocode(location: str) -> str:
    token = mapbox_token
    #build url
    base_url = 'https://api.mapbox.com/search/geocode/v6/forward'
    encoded_location = urllib.parse.quote(location)
    #final url built
    url = f"{base_url}?q={encoded_location}&access_token={token}"

    #opening aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    #this returns the entire json from mapbox geocoding
    return data

#post static map with location + red pin
@tree.command(name="staticmap", description="Posts an image of inputted location")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def staticmap(interaction: discord.Interaction, location: str):
    token = mapbox_token
    #grabbing location string from user
    geo = await geocode(location)

    #IF GEO IS EMPTY because location could not be found by mapbox
    if not geo["features"]:
        await interaction.response.send_message("Location not found. Try something else.")
        return
    #otherwise, grab all the good features
    feature = geo["features"][0]
    props = feature["properties"]
    address = props.get("full_address", "Unknown location")
    coords = props["coordinates"]

    lon = coords["longitude"]
    lat = coords["latitude"]
    #building url, break it into variables like this so its easier to read, easier to modify later
    base_url = 'https://api.mapbox.com/styles/v1/mapbox/streets-v12/static'
    overlay = f"pin-s+ff0000({lon},{lat})" #adding a red pin
    size = "600x400"
    url = f"{base_url}/{overlay}/{lon},{lat},13,0/{size}?access_token={token}"
    #aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            img_bytes = await resp.read()

    #not embedding due to discord compressing preview
    file = discord.File(io.BytesIO(img_bytes), filename="map.png")

    #sending the message if successful
    await interaction.response.send_message(content=f"📍 **{address}**", file=file)

    #url format v, actually just go into their playbox, find random location, then use the GET request
    #https://api.mapbox.com/styles/v1/{username}/{style_id}/static/{overlay}/{lon},{lat},{zoom},{bearing},{pitch}|{auto}|{bbox}/{width}x{height}{padding}{@2x}?access_token=token

#add map directions from mapbox, directions here to there

client.run(discord_token)