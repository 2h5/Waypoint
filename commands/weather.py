import discord
import aiohttp
from discord import app_commands
from utils.geocode import geocode

WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌦️"),
    56: ("Light freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Light freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "🌨️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}

def setup(tree):
    @tree.command(name="weather", description="Current weather for a location")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def weather(interaction: discord.Interaction, location: str):
        await interaction.response.defer()

        geo = await geocode(location)
        if not geo.get("features"):
            await interaction.followup.send("Location not found. Try something else.")
            return

        feature = geo["features"][0]
        props = feature["properties"]
        address = props.get("full_address", "Unknown location")
        coords = props["coordinates"]
        lon = coords["longitude"]
        lat = coords["latitude"]

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            "weather_code,wind_speed_10m"
            "&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=auto"
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
        except Exception as e:
            await interaction.followup.send(f"Error retrieving weather: {e}")
            return

        current = data.get("current")
        if not current:
            await interaction.followup.send("Weather data unavailable for that location.")
            return

        code = current.get("weather_code", 0)
        description, emoji = WEATHER_CODES.get(code, ("Unknown", "❓"))

        temp = current.get("temperature_2m")
        feels = current.get("apparent_temperature")
        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m")

        embed = discord.Embed(
            title=f"{emoji} {description}",
            description=f"📍 **{address}**",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Temperature", value=f"{temp}°F", inline=True)
        embed.add_field(name="Feels like", value=f"{feels}°F", inline=True)
        embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="Wind", value=f"{wind} mph", inline=True)

        await interaction.followup.send(embed=embed)
