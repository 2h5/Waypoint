import os
import aiohttp
import urllib.parse


async def geocode(location: str) -> str:
    token = os.getenv("MAPBOX_TOKEN")
    #build url
    base_url = 'https://api.mapbox.com/search/geocode/v6/forward'
    encoded_location = urllib.parse.quote(location)
    #final url built
    url = f"{base_url}?q={encoded_location}&access_token={token}"

    #opening aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    #this returns the entire json from mapbox geocoding
    return data