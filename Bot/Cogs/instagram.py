from discord.ext import commands
from instagram_private_api import Client, ClientCompatPatch
from dotenv import load_dotenv
load_dotenv()
import os
import discord

user_name = os.getenv('InstagramUserName')
password = os.getenv('InstagramPassword')

api = Client(user_name, password)
api.generate_uuid()
# will only output metadata
class instagram(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="iginfo")
    async def on_message(self, ctx, search:str):
        username_feed = api.user_info(search)
        embedVar = discord.Embed()
        embedVar.description = f'{username_feed}'
        await ctx.send(embed = embedVar)

class iguserfeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="iguserfeed")
    async def on_message(self, ctx, search:str):
        user_feed = api.user_feed(search)
        await ctx.send(user_feed)

class iginfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="igusersearch")
    async def on_message(self, ctx, search:str):
        top_search = api.search_users(search)
        embedVar = discord.Embed()
        embedVar.description = f'{top_search}'
        await ctx.send(embed = embedVar)

class top_search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="igtopsearch")
    async def on_message(self, ctx, search:str):
        best_search = api.top_search(search)
        embedVar = discord.Embed()
        embedVar.description = f'{best_search}'
        await ctx.send(embed = embedVar)
        
def setup(bot):
    bot.add_cog(instagram(bot))
    bot.add_cog(iguserfeed(bot))
    bot.add_cog(iginfo(bot))
    bot.add_cog(top_search(bot))