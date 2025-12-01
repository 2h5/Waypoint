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
   
        geo = await geocode(location)

   
        if not geo["features"]:
            await interaction.response.send_message("Location not found. Try something else.")
            return
    
        feature = geo["features"][0]
        props = feature["properties"]
        address = props.get("full_address", "Unknown location")
        coords = props["coordinates"]

        lon = coords["longitude"]
        lat = coords["latitude"]
  
        base_url = 'https://api.mapbox.com/styles/v1/mapbox/streets-v12/static'
        overlay = f"pin-s+ff0000({lon},{lat})" #adding a red pin
        size = "600x400"
        url = f"{base_url}/{overlay}/{lon},{lat},13,0/{size}?access_token={token}"
  
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    image = await response.read()
        except Exception as e:
            await interaction.response.send_message(f"Error retrieving map image: {e}")
            return

        file = discord.File(io.BytesIO(image), filename="map.png")

        await interaction.response.send_message(content=f"📍 **{address}**", file=file)

  