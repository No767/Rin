import asyncio
import datetime
import platform
import time

import discord
import uvloop
from discord.commands import SlashCommandGroup
from discord.ext import commands

RIN_VERSION = "2.2.8"


class Rin(commands.Cog):
    """Basic commands for Rin"""

    def __init__(self, bot):
        self.bot = bot

    rin = SlashCommandGroup("rin", "Commands for anything about Rin")

    @commands.Cog.listener()
    async def on_ready(self):
        global startTime
        startTime = time.time()

    @rin.command(name="uptime")
    async def botUptime(self, ctx):
        """Returns how long Rin has been online for"""
        uptime = datetime.timedelta(seconds=int(round(time.time() - startTime)))
        embed = discord.Embed(color=discord.Color.from_rgb(245, 227, 255))
        embed.description = f"Rin's Uptime: `{uptime.days} Days, {uptime.seconds//3600} Hours, {(uptime.seconds//60)%60} Minutes, {(uptime.seconds%60)} Seconds`"
        await ctx.respond(embed=embed)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @rin.command(name="stats")
    async def rinStats(self, ctx):
        """Displays some basic stats about Rin"""
        embed = discord.Embed()
        embed.title = self.bot.user.name
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Total Users", value=len(self.bot.users), inline=True)
        embed.add_field(
            name="Ping", value=f"{self.bot.latency*1000:.2f}ms", inline=True
        )
        embed.add_field(name="Rin's Version", value=f"v{RIN_VERSION}", inline=True)
        embed.add_field(
            name="Python Version", value=platform.python_version(), inline=True
        )
        embed.add_field(name="Pycord Version", value=discord.__version__, inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        await ctx.respond(embed=embed)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @rin.command(name="invite")
    async def rinInvite(self, ctx):
        """Returns invite link for Rin"""
        embedVar = discord.Embed()
        embedVar.description = "[Top.gg](https://top.gg/bot/865883525932253184/invite)"
        embedVar.set_author(name="Invite", icon_url=self.bot.user.display_avatar)
        await ctx.respond(embed=embedVar)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @rin.command(name="ping")
    async def rinPing(self, ctx):
        """Returns Rin's ping"""
        await ctx.respond(
            embed=discord.Embed(description=f"Ping: {self.bot.latency*1000:.2f}ms")
        )

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @rin.command(name="version")
    async def rinVersion(self, ctx):
        """Returns Rin's current version"""
        embedVar = discord.Embed()
        embedVar.description = f"Build Version: v{RIN_VERSION}"
        await ctx.respond(embed=embedVar)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def setup(bot):
    bot.add_cog(Rin(bot))
