import os
import discord
import io
import aiohttp
from discord import app_commands
from utils.geocode import geocode



def setup(tree):
    @tree.command(name="staticmap", description="Posts an image of inputted location")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def staticmap(interaction: discord.Interaction, location: str):
        token = os.getenv("MAPBOX_TOKEN")
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
        #response.json() parses json response
        #response.text() would get raw text
        #response.read() would get raw bytes
        #these comes from ahiohttp, mapbox tells us what the return is like if that returns a json, or image, etc
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    image = await response.read()
        except Exception as e:
            await interaction.response.send_message(f"Error retrieving map image: {e}")
            return

        #not embedding due to discord compressing preview
        file = discord.File(io.BytesIO(image), filename="map.png")

        #sending the message if successful
        await interaction.response.send_message(content=f"📍 **{address}**", file=file)

        #url format v, actually just go into their playbox, find random location, then use the GET request
        #https://api.mapbox.com/styles/v1/{username}/{style_id}/static/{overlay}/{lon},{lat},{zoom},{bearing},{pitch}|{auto}|{bbox}/{width}x{height}{padding}{@2x}?access_token=token