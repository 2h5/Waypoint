import os
import discord
import io
import aiohttp
from discord import app_commands
from utils.geocode import geocode
from utils.static_map_util import static_map_util
from utils.format_duration import format_duration

def setup(tree):
 #add map directions from mapbox, directions here to there
    @tree.command(name="route", description="start to destination planner")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def route(interaction: discord.Interaction, start: str, end: str):
        #since discord times out too quickly
        await interaction.response.defer()
        
        token = os.getenv("MAPBOX_TOKEN")
        geo_start = await geocode(start)
        geo_end = await geocode(end)
        
        start_name = geo_start["features"][0]["properties"].get("name_preferred", start)
        end_name = geo_end["features"][0]["properties"].get("name_preferred", end)
        
        if not geo_start["features"] or not geo_end["features"]:
            await interaction.followup.send("Location(s) not found. Try something else.")
            return
        
        start_point = geo_start["features"][0]["geometry"]["coordinates"]
        end_point = geo_end["features"][0]["geometry"]["coordinates"]
        
        lon1 = start_point[0]
        lat1 = start_point[1]
        lon2 = end_point[0]
        lat2 = end_point[1]
        
        get_map = f"https://api.mapbox.com/directions/v5/mapbox/driving/{lon1}%2C{lat1}%3B{lon2}%2C{lat2}?alternatives=false&annotations=distance%2Cduration&geometries=polyline&overview=full&steps=false&access_token={token}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(get_map) as response:
                    if response.status != 200:
                        await interaction.followup.send("The route is too long, crosses unsupported areas, or exceeds Mapbox's limits.")
                        return
                    try:
                        directions_json = await response.json()
                    except aiohttp.ContentTypeError:
                        await interaction.followup.send("Mapping service returned invalid response (HTML or empty).")
                        return

            except Exception as e:
                await interaction.followup.send(f"Error retrieving route: {e}")
                return

        if not directions_json["routes"]:
            await interaction.followup.send("No route found. Try different locations.")
            return
        
        dur = directions_json["routes"][0]["duration"] / 60
        duration = format_duration(dur)
        
        dis = directions_json["routes"][0]["distance"]
        distance = dis/1609.34      

        summary = directions_json["routes"][0]["legs"][0]["summary"]

        polyline = directions_json["routes"][0]["geometry"]

        map = await static_map_util(start=(lon1,lat1), end=(lon2,lat2), polyline_str=polyline, width=1280, height=720)
        
                
        file = discord.File(io.BytesIO(map), filename="route.png")
        await interaction.followup.send(content=f"**Route:** {start_name} **→** {end_name}\n" f"**Summary:** {summary}\n"f"**Distance:** {distance:.1f} mile(s)\n"f"**Duration:** {duration}", file=file)
        
        
        
      

    