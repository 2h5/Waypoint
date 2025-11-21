import os
import discord
from discord import app_commands

def setup(tree):
    @tree.command(name="good", description = "ez")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def image_good(interaction: discord.Interaction):
        folder = "images"
        path = os.path.join(folder, "good.jpg")
    
        with open(path, "rb") as f:
            picture = discord.File(f)
            await interaction.response.send_message(file=picture)