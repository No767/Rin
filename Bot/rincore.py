import logging
import os
from pathlib import Path

import discord
from discord.ext import tasks


class RinCore(discord.Bot):
    """Rin's Core - Now subclassed"""

    def __init__(self, *args, **kwargs):
        """Rin's Core - Now subclassed"""
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("rinbot")
        self.loadCogs()

    def loadCogs(self):
        """Rin's system to load cogs"""
        path = Path(__file__).parent
        cogsPath = path / "Cogs"
        cogsList = os.listdir(cogsPath)
        for items in cogsList:
            if items.endswith(".py") and not items[:-3] == "models":
                self.load_extension(f"Cogs.{items[:-3]}")
                self.logger.debug(f"Loaded Cog: {items[:-3]}")

    @tasks.loop(count=1)
    async def statusMessage(self):
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="/help")
        )

    @statusMessage.before_loop
    async def beforeReady(self):
        await self.wait_until_ready()

    async def on_ready(self):
        self.logger.info(f"{self.user.name} is ready to go!")
