import os
from db import database

# Revo api endpoint
API_ENDPOINT = os.environ["REVO_API"]

# Dictionary of WA gym locations
LOCATIONS = {
    "canning vale": ("canning_vale.json", 2000),
    "claremont": ("claremont_count.json", 1370),
    "kelmscott": ("kelmscott_count.json", 760),
    "myaree": ("myaree_count.json", 860),
    "northbridge": ("northbridge_count.json", 865),
    "oconnor": ("oconnor_count.json", 1081),
    "scarborough": ("scarbs_count.json", 920),
    "shenton park": ("shenton_count.json", 550),
    "victoria park": ("vic_count.json", 1100),
    "innaloo": ("innaloo.json", 1767),
    "cockburn": ("cockburn.json", 1000),
    "joondalup": ("joondalup.json", 1990),
    "mirrabooka": ("mirrabooka.json", 2400),
    "belmont": ("belmont.json", 1050),
    "banksia grove": ("banksia_grove.json", 1100),
    "morley": ("morley_count.json", 1800)
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
