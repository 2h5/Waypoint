import os
import discord
import io
import aiohttp
from discord import app_commands
from utils.geocode import geocode





def setup(tree):
 #add map directions from mapbox, directions here to there
    @tree.command(name="route", description="start to destination planner")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def route(interaction: discord.Interaction, start: str, end: str):
        token = os.getenv("MAPBOX_TOKEN")
        geo_start = await geocode(start)
        geo_end = await geocode(end)

        if not geo_start["features"] or not geo_end["features"]:
            await interaction.response.send_message("Route/location(s) not found. Try something else.")
            return

        
        await interaction.response.send_message("Waiting..")