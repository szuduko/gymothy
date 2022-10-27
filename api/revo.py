import os

# Revo api endpoint
API_ENDPOINT = os.environ["REVO_API"]

# Dictionary of WA gym locations
LOCATIONS = {
    "Banksia Grove": ("banksia-grove.json", 1100),
    "Belmont": ("belmont.json", 1050),
    "Canning Vale": ("canning-vale.json", 2000),
    "Claremont": ("claremont.json", 1370),
    "Cockburn": ("cockburn.json", 1000),
    "Innaloo": ("innaloo.json", 1767),
    "Joondalup": ("joondalup.json", 1990),
    "Kelmscott": ("kelmscott.json", 760),
    "Mirrabooka": ("mirrabooka.json", 2400),
    "Morley": ("morley.json", 1800),
    "Myaree": ("myaree.json", 860),
    "Northbridge": ("northbridge.json", 865),
    "O'Connor": ("oconnor.json", 1081),
    "Scarborough": ("scarborough.json", 920),
    "Shenton Park": ("shenton-park.json", 550),
    "Victoria Park": ("victoria-park.json", 1100)
}


# Utility function to get the live member count of a given location
async def get_count(session, location):
    """Get the live member count of the specified location"""

    url = str(API_ENDPOINT) + str(LOCATIONS[location][0])

    async with session.get(url) as response:
        count = await response.json()
        if count == None:
            count = 0
    return location, count
