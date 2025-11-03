import discord
from discord import app_commands
from deep_translator import GoogleTranslator
from datetime import datetime
import os

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
            "Error, check your language code (it's 2 character codes)."
        )
        print(f"[{now}] ❌ {username} tried lang='{lang}'")
#uploads 6 7 ¬‿¬
@tree.command(name="sixseven", description = "6 7 uploader")
async def image_six_seven(interaction: discord.Interaction):
    folder = "images"
    path = os.path.join(folder, "6 7.webp")
   
    with open(path, "rb") as f:
        picture = discord.File(f)
        await interaction.response.send_message(file=picture)
#uploads speed laugh
@tree.command(name="speed", description = "yoo")
async def image_speed(interaction: discord.Interaction):
    folder = "images"
    path = os.path.join(folder, "image8.jpg")
   
    with open(path, "rb") as f:
        picture = discord.File(f)
        await interaction.response.send_message(file=picture)
#uploads this guy
@tree.command(name="good", description = "ez")
async def image_good(interaction: discord.Interaction):
    folder = "images"
    path = os.path.join(folder, "good.jpg")
   
    with open(path, "rb") as f:
        picture = discord.File(f)
        await interaction.response.send_message(file=picture)

#bot token down here :[] ur not allowed to see this if ur not me
client.run("REDACTED")