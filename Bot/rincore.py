import logging
from pathlib import Path
from typing import Dict

import discord
from discord.ext import ipc
from discord.ext.ipc.objects import ClientPayload
from discord.ext.ipc.server import Server


class RinCore(discord.Bot):
    """Rin's Core - Now subclassed"""

    def __init__(self, *args, **kwargs):
        """Rin's Core - Now subclassed"""
        super().__init__(
            activity=discord.Activity(type=discord.ActivityType.watching, name="/help"),
            *args,
            **kwargs,
        )
        self.ipc = ipc.Server(self, secret_key="test")  # nosec
        self.logger = logging.getLogger("rinbot")
        self.loadCogs()
        self.loop.create_task(self.ipc.start())

    def loadCogs(self):
        """Rin's system to load cogs"""
        cogsPath = Path(__file__).parent.joinpath("Cogs")
        for cog in cogsPath.rglob("*.py"):
            self.load_extension(f"Cogs.{cog.name[:-3]}")
            self.logger.debug(f"Loaded Cog: {cog.name[:-3]}")

    async def on_ready(self):
        self.logger.info(f"{self.user.name} is ready to go!")

    @Server.route()
    async def get_user_data(self, data: ClientPayload) -> Dict:
        user = self.get_user(data.user_id)
        return user._to_minimal_user_json()
        # return {"message": "yes"}

    @Server.route()
    async def get_all_commands(self, data: ClientPayload) -> Dict:
        allCommands = [
            {
                "name": items.qualified_name,
                "description": items.description,
                "module": items.module.replace("Cogs.", "")
                if items.module != "discord.commands.core"
                else "None",
                "parent_name": items.parent.name
                if items.parent is not None
                else "None",
            }
            for items in self.walk_application_commands()
        ]
        return {"count": len(allCommands), "data": allCommands}

    @Server.route()
    async def get_command(self, data: ClientPayload) -> Dict:
        command = self.get_application_command(data.name)
        return {
            "name": command.qualified_name,
            "description": command.description,
            "module": command.module.replace("Cogs.", "")
            if command.module != "discord.commands.core"
            else "None",
            "parent_name": command.parent.name
            if command.parent is not None
            else "None",
        }

    @Server.route()
    async def get_all_cogs(self, data: ClientPayload) -> Dict:
        allCogs = [
            {"name": cogName, "description": cog.__doc__}
            for cogName, cog in self.cogs.items()
            if cogName not in ["InteractionFailureHandler", "IPCServer"]
        ]
        return {"count": len(allCogs), "cogs": allCogs}

    @Server.route()
    async def get_cog(self, data: ClientPayload) -> Dict:
        cog = await self.get_cog(data.name)
        return {"name": cog.qualified_name, "description": cog.description}
