import traceback

import discord
from discord.ext import commands


class InteractionFailureHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def fullException(self, obj):
        module = obj.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return obj.__class__.__name__
        return module + "." + obj.__class__.__name__

    @commands.Cog.listener()
    async def on_application_command_error(
        self, ctx: discord.ApplicationContext, error: discord.DiscordException
    ):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = int(error.retry_after) % (24 * 3600)
            hours = seconds // 3600
            seconds %= 3600
            minutes = seconds // 60
            seconds %= 60
            await ctx.respond(
                embed=discord.Embed(
                    description=f"This command is currently on cooldown. Try again in {hours} hour(s), {minutes} minute(s), and {seconds} second(s)."
                )
            )
        elif isinstance(error, commands.MissingPermissions):
            missingPerms = (
                str(error.missing_permissions)
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
            )
            await ctx.respond(
                embed=discord.Embed(
                    description=f"You are missing the following permissions: {missingPerms}"
                )
            )
        elif isinstance(error, commands.BotMissingPermissions):
            missingPerms = (
                str(error.missing_permissions)
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
            )
            await ctx.respond(
                embed=discord.Embed(
                    description=f"Kumiko is missing the following permissions: {missingPerms}"
                )
            )
        elif isinstance(error, discord.ApplicationCommandInvokeError):
            errorEmbed = discord.Embed(
                title="An error has occured",
                color=discord.Color.from_rgb(255, 41, 41),
            )
            errorEmbedHeader = "Uh oh! It seems like the command ran into an issue! For support, please issue an issue report on the [GitHub issues tracker](https://github.com/No767/Rin/issues)"
            errorEmbed.description = f"{errorEmbedHeader}\n\n**Error:** ```{error.original}```\n**Full Exception Message:**\n```{self.fullException(error.original)}: {str(error.original)}```\n**Full Debug Traceback:**\n```{traceback.format_exc()}```"
            await ctx.respond(embed=errorEmbed)


def setup(bot):
    bot.add_cog(InteractionFailureHandler(bot))
