#!/usr/bin/env python3
import logging
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Grabs the bot's token from the .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] | %(asctime)s >> %(message)s",
    datefmt="[%m/%d/%Y] [%I:%M:%S %p %Z]",
)

TOKEN = os.getenv("Rin_Prod_Testing_Key")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", help_command=None, intents=intents)

# Loads in all extensions
initial_extensions = [
    # "Cogs.rininfo",
    # "Cogs.rinping",
    # "Cogs.rinhelp",
    "Cogs.reddit",
    # "Cogs.mcsrvstats",
    # "Cogs.waifu-generator",
    # "Cogs.waifu-pics",
    # "Cogs.advice",
    # "Cogs.jikan",
    # "Cogs.global-error-handling",
    # "Cogs.rininvite",
    # "Cogs.version",
    # "Cogs.youtube",
    # "Cogs.tenor",
    # "Cogs.uptime",
    # "Cogs.mangadex",
    # "Cogs.bot-info",
    # "Cogs.help",
    # "Cogs.modrinth",
    # "Cogs.discord-bots",
    # "Cogs.legacy-help",
    # "Cogs.jisho",
    # "Cogs.anilist"
]
for extension in initial_extensions:
    bot.load_extension(extension)


# Adds in the bot presence
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/rinhelp"))

# Run the bot
bot.run(TOKEN)
