import os
import math
import datetime
import aiohttp
import asyncio
import discord
from discord.ext import commands
from api import revo

TOKEN = os.environ["DISCORD_TOKEN"]
PREFIX = "-"

intents = discord.Intents(messages=True,
                          guilds=True,
                          reactions=True,
                          message_content=True)

bot = commands.Bot(command_prefix=PREFIX,
                   case_insensitive=True,
                   intents=intents)

bot.author_id = 262853566983700482

# Estimated 60% unusable area (reception, walkways, bathrooms, etc)
UNUSABLE_AREA_RATE = 0.40
# 10 sq metres per person for comfortable experience
MIN_PERSONAL_SPACE = 10


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


# Get a specific gym
@bot.command(name="gym",
             aliases=["g"],
             help="This is help text",
             description="This is a description")
async def gym(ctx, *, location):
    """Get a specific gym"""

    async with ctx.typing():

        # Check if the location is a valid gym location
        gym_location = location.lower()
        if gym_location in list(revo.LOCATIONS.keys()):

            # Query revo api
            async with aiohttp.ClientSession() as session:
                tasks = []
                task = asyncio.ensure_future(
                    revo.get_count(session, gym_location))
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
            embed.add_field(
                name="__Personal Space__",
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

    await ctx.send(embed=embed)


# Get all gyms
@bot.command(name="gyms",
             help="This is help text",
             description="This is a description")
async def gyms(ctx):
    """Get all gyms"""

    async with ctx.typing():

        # Query revo api
        async with aiohttp.ClientSession() as session:
            tasks = []
            for key in revo.LOCATIONS:
                task = asyncio.ensure_future(revo.get_count(session, key))
                tasks.append(task)
            gyms = await asyncio.gather(*tasks)

        # Create embed heading
        embed = discord.Embed(
            title="Every Location",
            description="Live member count of each location...",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow())

        # Create each gym's live count field
        for gym in gyms:
            noun = "person" if gym[1] == 1 else "people"
            embed.add_field(name=f"__{str(gym[0]).title()}__",
                            value=f"**{gym[1]}** *{noun}*",
                            inline=True)

    await ctx.send(embed=embed)


bot.run(TOKEN, reconnect=True)
