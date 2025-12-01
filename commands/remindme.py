import discord
from discord import app_commands
from datetime import datetime
import re
import asyncio


def setup(tree):
    @tree.command(name="remindme", description="Set a reminder for yourself")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def remindme(interaction: discord.Interaction, time: str, *, text: str):
       
        # /remindme time: 10m text: take out the trash
        # Supported units: s (seconds), m (minutes), h (hours)
       
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