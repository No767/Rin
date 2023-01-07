import logging
import os

import discord
import uvloop
from dotenv import load_dotenv
from rincore import RinCore

# Grabs the bot's token from the .env file
load_dotenv()

TOKEN = os.getenv("Testing_Bot_Token")
intents = discord.Intents.default()
intents.message_content = True
bot = RinCore(intents=intents)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] | %(asctime)s >> %(message)s",
    datefmt="[%m/%d/%Y] [%I:%M:%S %p %Z]",
)
logging.getLogger("gql").setLevel(logging.WARNING)

if __name__ == "__main__":
    uvloop.install()
    bot.run(TOKEN)
