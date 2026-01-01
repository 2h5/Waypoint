import os
import asyncio
import aiohttp
import discord
from discord import app_commands


USPS_USER_ID = os.getenv("USPS_USER_ID")  
POLL_INTERVAL = 600


active_trackers = {}


def setup(tree):
    @tree.command(name="tracking", description="Show USPS packages currently being tracked")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def tracking(interaction: discord.Interaction):
        if not active_trackers:
            await interaction.response.send_message(
                "📭 No USPS packages are currently being tracked.",
                ephemeral=True,
            )
            return

        lines = []
        for tn, data in active_trackers.items():
            status = data.get("last_status") or "⏳ Waiting for first update…"
            lines.append(f"• **{tn}**\n  {status}")

        message = "📦 **Currently tracking:**\n\n" + "\n".join(lines)

        await interaction.response.send_message(
            message,
            ephemeral=True,
        )
   

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

            
            #test
            print(f"Parsed status for {tracking_number}: {status}")
            
            
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
    def extract(marker: str) -> str | None:
        start = html.find(marker)
        if start == -1:
            return None

        start += len(marker)
        end = html.find("</p>", start)
        if end == -1:
            return None

        text = html[start:end]
        return text.replace("&nbsp;", " ").strip()

    main = extract('<p class="tb-status">')
    if not main:
        return None

    detail = extract('<p class="tb-status-detail">')
    location = extract('<p class="tb-location">')

    parts = [main]

    if detail:
        parts.append(detail)

    if location:
        parts.append(f"📍 {location}")

    return " — ".join(parts)


    