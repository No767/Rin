import discord
from discord.ext import commands
from searchtweets import load_credentials
import os
from dotenv import load_dotenv

load_dotenv()

Twitter_API_Key = os.getenv("Twitter_API_Key")
API_Secret_Key = os.getenv("API_Secret_Key")
Access_Token = os.getenv("Access_Token")
Access_Token_Secret = os.getenv("Access_Token_Secret")


load_credentials()