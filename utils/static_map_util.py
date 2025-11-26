import os
import aiohttp
from urllib.parse import quote
import polyline

async def static_map_util(start=None, end=None, polyline_str=None, width=1280, height=720, padding=None):
    token = os.getenv("MAPBOX_TOKEN")
    #keeping a list of all overlay options we want to add, 
    overlays = [] 
    
    if start:
        overlays.append(f"pin-s+FF0000({start[0]},{start[1]})")
    if end:
        overlays.append(f"pin-s+0000FF({end[0]},{end[1]})")
#-------------------------------------------------------------------
    #reduced polyline. Geometry characters blew up on state to state
    if polyline_str:
        try:
            coords = polyline.decode(polyline_str)
        except Exception:
            coords = None

    if coords:
        n = len(coords)
        if n <= 200:            
            step = 1           
        elif n <= 500:        
            step = 2
        elif n <= 1500:        
            step = 5
        elif n <= 3000:       
            step = 10
        elif n <= 6000:       
            step = 20
        else:                 
            step = 50

        reduced = coords[::step]
        simple_poly = polyline.encode(reduced)

        encoded_poly = quote(simple_poly, safe='')
    else:
        encoded_poly = quote(polyline_str, safe='')

    overlays.append(f"path-5+0000FF({encoded_poly})")
#--------------------------------------------------------------------
    overlay = ",".join(overlays)
 
    url = (
        f"https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/"
        f"{overlay}/auto/{width}x{height}?access_token={token}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
    return data