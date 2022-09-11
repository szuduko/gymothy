import os
import math
import datetime
import aiohttp
import asyncio
import discord
from discord import app_commands
from discord.app_commands import Choice
from api import revo

# Estimated 60% unusable area (reception, walkways, bathrooms, etc)
UNUSABLE_AREA_RATE = 0.40
# 10 sq metres per person for comfortable experience
MIN_PERSONAL_SPACE = 10


class sub_client(discord.Client):

    def __init__(self):
        super().__init__(intents=discord.Intents.default(),
                         activity=discord.Activity(
                             type=discord.ActivityType.listening,
                             name="Farting and Screaming"),
                         status=discord.Status.online)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print(f"{self.user} has connected to Discord!")


client = sub_client()
tree = app_commands.CommandTree(client)

choices = []

for location in revo.LOCATIONS.keys():
    choices.append(Choice(name=str(location), value=str(location)))


# Get a specific gym
@tree.command(name="gym", description="Get a specific gym")
@app_commands.describe(location="Gym location")
@app_commands.choices(location=choices)
async def gym(interaction: discord.Interaction, location: str):
    """Get a specific gym"""

    # Check if the location is a valid gym location
    gym_location = location.lower()
    if gym_location in list(revo.LOCATIONS.keys()):

        # Query revo api
        async with aiohttp.ClientSession() as session:
            tasks = []
            task = asyncio.ensure_future(revo.get_count(session, gym_location))
            tasks.append(task)
            gym = await asyncio.gather(*tasks)

        # Create embed heading
        embed = discord.Embed(title=f"{str(gym[0][0]).title()}",
                              color=discord.Color.green(),
                              timestamp=datetime.datetime.utcnow())

        # Create embed Live Count field
        noun = "person" if gym[0][0] == 1 else "people"
        embed.add_field(name="__Live Count__",
                        value=f"**{gym[0][1]}** *{noun}*")

        # Create embed Area field
        area = revo.LOCATIONS[gym[0][0]][1]
        embed.add_field(name="__Area__",
                        value=f"{area:.2f} *sq metres*",
                        inline=False)

        # Create embed Usable Area field
        usable_area = (area * UNUSABLE_AREA_RATE)
        embed.add_field(name="__Estimated Usable Area__",
                        value=f"{usable_area:.2f} *sq metres*",
                        inline=False)

        # Create embed Personal Space field
        personal_space = usable_area / max(gym[0][1], 1)
        embed.add_field(name="__Personal Space__",
                        value=f"{personal_space:.2f} *sq metres per person*",
                        inline=False)

        # Create embed Capacity field
        max_occupancy = math.floor(usable_area / MIN_PERSONAL_SPACE)
        embed.add_field(name="__Capacity__",
                        value=f"{((gym[0][1]/max_occupancy)*100):.2f}%",
                        inline=False)

    else:
        # Create embed heading
        embed = discord.Embed(color=discord.Color.red(),
                              timestamp=datetime.datetime.utcnow())

        # Create embed Error heading
        embed.add_field(name="__Error__",
                        value=f"Unable to identify the {gym_location} gym")

    # ephemeral=True
    await interaction.response.send_message(embed=embed)


# Get all gyms
@tree.command(name="gyms", description="Get all gyms")
async def gyms(interaction: discord.Interaction):
    """Get all gyms"""

    # Query revo api
    async with aiohttp.ClientSession() as session:
        tasks = []
        for key in revo.LOCATIONS:
            task = asyncio.ensure_future(revo.get_count(session, key))
            tasks.append(task)
        gyms = await asyncio.gather(*tasks)

    # Create embed heading
    embed = discord.Embed(title="Every Location",
                          description="Live member count of each location...",
                          color=discord.Color.green(),
                          timestamp=datetime.datetime.utcnow())

    # Create each gym's live count field
    for gym in gyms:
        noun = "person" if gym[1] == 1 else "people"
        embed.add_field(name=f"__{str(gym[0]).title()}__",
                        value=f"**{gym[1]}** *{noun}*",
                        inline=True)

    # ephemeral=True
    await interaction.response.send_message(embed=embed)


client.run(os.environ['DISCORD_TOKEN'])
