import os
import asyncio
import aiohttp
import discord
from discord import app_commands
from dotenv import load_dotenv
import datetime



load_dotenv()
POLL_INTERVAL = 600 

active_trackers: dict[str, dict] = {}

def parse_aftership_status(data: dict) -> str | None:
    meta = data.get("meta", {})
    code = meta.get("code")
    if code not in [200, 201, 4009, 4003]:
        raise ValueError(f"API Error [{code}]: {meta.get('message')}")

    raw_data = data.get("data", {})
    
    tracking = raw_data.get("tracking", raw_data)
    
    if not tracking:
        return "Status Unknown (No Data)"

    tag = tracking.get("tag")
    subtag = tracking.get("subtag")
    checkpoint = tracking.get("checkpoint") or {}
    location = checkpoint.get("location")

    parts = []
    
    if tag == "Pending":
        return "⏳ **Pending** (Syncing with USPS...)"

    if tag:
        parts.append(tag.replace("_", " ").title())

    if subtag:
        parts.append(subtag.replace("_", " ").title())

    if location:
        parts.append(f"📍 {location}")

    return " — ".join(parts) if parts else "Status Unknown"

async def poll_aftership(client: discord.Client, tracking_number: str):
    tracking_number = tracking_number.strip()
    api_key = os.getenv("AFTERSHIP_API_KEY")
    
    headers = {
        "as-api-key": api_key,
        "Content-Type": "application/json"
    }

    needs_registration = True
    slug = "usps" 

    while tracking_number in active_trackers:
        try:
            async with aiohttp.ClientSession() as session:
                if needs_registration:
                    url = "https://api.aftership.com/tracking/2024-04/trackings"
                    payload = {"tracking_number": tracking_number}

                    async with session.post(url, headers=headers, json=payload) as response:
                        data = await response.json()
                        code = data.get("meta", {}).get("code")
                        if code in [201, 4003, 4009]:
                            needs_registration = False
                            
                            tracking_data = data.get('data', {})
                            if 'tracking' in tracking_data:
                                tracking_data = tracking_data['tracking']
                            
                            found_slug = tracking_data.get('slug')
                            if found_slug:
                                slug = found_slug
                                
                            print(f"[AFTERSHIP] Tracking confirmed. Slug: {slug}")
                        
                        else:
                            print(f"[AFTERSHIP ERROR] Registration Failed. Code: {code}")
                            
                            if code in [4004, 4005, 4007]: 
                                await user_alert(client, tracking_number, f"⚠️ API Error: {data.get('meta', {}).get('message')}")
                                del active_trackers[tracking_number]
                                return
                            
                            await asyncio.sleep(POLL_INTERVAL)
                            continue

                else:
                    url = f"https://api.aftership.com/tracking/2024-04/trackings/{slug}/{tracking_number}"
                    
                    async with session.get(url, headers=headers) as response:
                        data = await response.json()
                        if data.get("meta", {}).get("code") != 200:
                            print(f"[AFTERSHIP WARNING] GET returned {data.get('meta', {}).get('code')}. Re-registering...")
                            needs_registration = True
                            continue

    
                status = parse_aftership_status(data)
                tracker = active_trackers.get(tracking_number)
                if not tracker: return

                old_status = tracker["last_status"]
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")

                print(f"[{timestamp}] Checking {tracking_number}...")
                print(f"   Saved Status:  {old_status}")
                print(f"   API Status:    {status}")
                
                if old_status == status:
                    print(f"   Result:        NO CHANGE (Sleeping for {POLL_INTERVAL}s)")
                else:
                    print(f"   Result:        >>> UPDATE DETECTED! <<<")

                if status and old_status != status:
                    tracker["last_status"] = status
                    await user_alert(client, tracking_number, f"📦 **Update for {tracking_number}:**\n{status}")

                    if "Delivered" in status:
                        del active_trackers[tracking_number]
                        return

        except Exception as e:
            print(f"[AFTERSHIP EXCEPTION] {tracking_number}: {e}")
            import traceback
            traceback.print_exc()

        await asyncio.sleep(POLL_INTERVAL)

async def user_alert(client, tracking_number, message):
    tracker = active_trackers.get(tracking_number)
    if not tracker: return
    try:
        user = await client.fetch_user(tracker["user_id"])
        await user.send(message)
    except discord.Forbidden:
        pass

def setup(tree: app_commands.CommandTree):

    @tree.command(name="trackusps", description="Track a USPS package and DM updates")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def trackusps(interaction: discord.Interaction, tracking_number: str):
        await interaction.response.defer(ephemeral=True)

        if tracking_number in active_trackers:
            await interaction.followup.send(
                "That tracking number is already being monitored.",
                ephemeral=True,
            )
            return

        active_trackers[tracking_number] = {
            "last_status": None,
            "user_id": interaction.user.id,
        }

        await interaction.followup.send(
            f"Started tracking **{tracking_number}**.\n"
            "I’ll DM you when the status changes.",
            ephemeral=True,
        )

        interaction.client.loop.create_task(
            poll_aftership(interaction.client, tracking_number)
        )

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
