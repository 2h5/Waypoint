import os
import aiohttp
import urllib.parse


async def geocode(location: str) -> str:
    token = os.getenv("MAPBOX_TOKEN")
   
    base_url = 'https://api.mapbox.com/search/geocode/v6/forward'
    encoded_location = urllib.parse.quote(location)
 
    url = f"{base_url}?q={encoded_location}&access_token={token}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    return data