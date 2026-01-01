import os
import asyncio
import aiohttp
import discord
from discord import app_commands


USPS_USER_ID = os.getenv("USPS_USER_ID")  
POLL_INTERVAL = 600


active_trackers = {}


def setup(tree):

    @tree.command(name="trackusps", description="Track a USPS package and DM updates")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def trackusps(interaction: discord.Interaction, tracking_number: str):
        await interaction.response.defer(ephemeral=True)

        user = interaction.user

        if tracking_number in active_trackers:
            await interaction.followup.send(
                "That tracking number is already being monitored."
            )
            return

        active_trackers[tracking_number] = {
            "last_status": None,
            "user_id": user.id,
        }

        await interaction.followup.send(
            f"Started tracking **{tracking_number}**.\n"
            "I’ll DM you when the status changes."
        )

    
        interaction.client.loop.create_task(
            poll_usps(interaction.client, tracking_number)
        )


async def poll_usps(client: discord.Client, tracking_number: str):
    url = "https://tools.usps.com/go/TrackConfirmAction_input"

    while tracking_number in active_trackers:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params={"tLabels": tracking_number},
                    headers={"User-Agent": "Mozilla/5.0"},
                ) as response:
                    text = await response.text()

            status = parse_status(text)

            if not status:
                await asyncio.sleep(POLL_INTERVAL)
                continue

            tracker = active_trackers.get(tracking_number)
            if not tracker:
                return

            if tracker["last_status"] != status:
                tracker["last_status"] = status

                user = await client.fetch_user(tracker["user_id"])
                await user.send(
                    f"📦 **USPS Update for {tracking_number}:**\n{status}"
                )

                if "Delivered" in status:
                    del active_trackers[tracking_number]
                    return

        except Exception:
            pass

        await asyncio.sleep(POLL_INTERVAL)


def parse_status(html: str) -> str | None:
    """
    Very lightweight parsing — good enough for one-off tracking.
    """
    marker = 'class="delivery_status">'
    if marker not in html:
        return None

    start = html.find(marker) + len(marker)
    end = html.find("</", start)
    return html[start:end].strip()