import asyncio

import discord
import uvloop
from discord.commands import slash_command
from discord.ext import commands


class HelpSelect(discord.ui.Select):
    def __init__(self, cog: commands.Cog) -> None:
        super().__init__(
            placeholder="Choose a category",
            options=[
                discord.SelectOption(
                    label=cog_name,
                    description=cog.__doc__,
                )
                for cog_name, cog in cog.bot.cogs.items()
                if cog_name not in ["InteractionFailureHandler", "IPCServer"]
            ],
        )
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        cog = self.cog.bot.get_cog(self.values[0])
        embed = discord.Embed(
            title=f"{cog.__cog_name__} Commands",
            description="\n".join(
                f"`/{command.qualified_name}`: {command.description}"
                for command in cog.walk_commands()
            ),
            color=discord.Color.from_rgb(189, 206, 255),
            timestamp=discord.utils.utcnow(),
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )


class Help(commands.Cog):
    """Commands for getting the commands for Rin"""

    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="help", description="The help command page for Rin")
    async def rinHelp(self, ctx):
        embed = discord.Embed(title=self.bot.user.name)
        embed.description = """
        Rin is a Discord bot focused on providing data from third party services such as Hypixel, Reddit, MyAnimeList/Jikan, and many others with lighting speed. Rin allows you to find memes on Reddit with the Reddit service, or get info about your favorite anime with the AniList service.\n
        Use the menu below to view commands.
        """
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(
            name="Server Count", value=str(len(self.bot.guilds)), inline=True
        )
        embed.add_field(name="User Count", value=str(len(self.bot.users)), inline=True)
        embed.add_field(
            name="Total Categories",
            value=str(
                len(
                    [
                        cogs
                        for cogs in self.bot.cogs
                        if cogs not in ["InteractionFailureHandler"]
                    ]
                )
            ),
            inline=True,
        )
        view = discord.ui.View(HelpSelect(self))
        await ctx.respond(embed=embed, view=view)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def setup(bot):
    bot.add_cog(Help(bot))
