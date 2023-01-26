import os
from datetime import datetime

import aiohttp
import ciso8601
import discord
import orjson
import simdjson
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands, pages
from dotenv import load_dotenv
from rin_exceptions import NoItemsError

load_dotenv()

API_KEY = os.getenv("Blue_Alliance_API_Key")
parser = simdjson.Parser()


class BlueAlliance(commands.Cog):
    """Commands for getting data from The Blue Alliance"""

    def __init__(self, bot):
        self.bot = bot

    blueAlliance = SlashCommandGroup("blue-alliance", "Blue Alliance API commands")
    blueAllianceMatches = blueAlliance.create_subgroup(
        "matches", "Blue Alliance match commands"
    )
    blueAllianceTeams = blueAlliance.create_subgroup(
        "teams", "Blue Alliance team commands"
    )

    @blueAllianceTeams.command(name="info")
    async def blueAllianceTeamInfo(
        self, ctx, *, team_number: Option(int, "The FRC team number")
    ):
        """Returns info about an FRC team"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {"X-TBA-Auth-Key": API_KEY}
            async with session.get(
                f"https://www.thebluealliance.com/api/v3/team/frc{team_number}",
                headers=headers,
            ) as r:
                try:
                    data = await r.content.read()
                    dataMain = parser.parse(data, recursive=True)
                    embed = discord.Embed()
                    if "Error" in dataMain:
                        raise NoItemsError
                    else:
                        embed.title = (
                            f"{dataMain['team_number']} - {dataMain['nickname']}"
                        )
                        embed.add_field(name="City", value=dataMain["city"])
                        embed.add_field(name="State", value=dataMain["state_prov"])
                        embed.add_field(name="Country", value=dataMain["country"])
                        embed.add_field(
                            name="Rookie Year", value=dataMain["rookie_year"]
                        )
                        embed.add_field(
                            name="Team Number", value=dataMain["team_number"]
                        )
                        embed.add_field(name="Team Website", value=dataMain["website"])
                        await ctx.respond(embed=embed)
                except NoItemsError:
                    embedError = discord.Embed()
                    embedError.description = "It seems like there are no teams named like that. Please try again"
                    await ctx.respond(embed=embedError)

    @blueAllianceTeams.command(name="events")
    async def blueAllianceTeamEvents(
        self, ctx, *, team_number: Option(int, "The FRC team number")
    ):
        """Returns what events an FRC team has attended"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {"X-TBA-Auth-Key": API_KEY}
            async with session.get(
                f"https://www.thebluealliance.com/api/v3/team/frc{team_number}/events",
                headers=headers,
            ) as r:
                data2 = await r.content.read()
                dataMain2 = parser.parse(data2, recursive=True)
                try:
                    if "Error" in dataMain2:
                        raise NoItemsError
                    else:
                        mainPages = pages.Paginator(
                            pages=[
                                discord.Embed(title=mainItem["name"])
                                .add_field(
                                    name="Event Location Address",
                                    value=mainItem["address"],
                                    inline=True,
                                )
                                .add_field(
                                    name="Event Location Name",
                                    value=mainItem["location_name"],
                                    inline=True,
                                )
                                .add_field(
                                    name="Event Key", value=mainItem["key"], inline=True
                                )
                                .add_field(
                                    name="Event Type",
                                    value=mainItem["event_type_string"],
                                    inline=True,
                                )
                                .add_field(
                                    name="Start Date",
                                    value=discord.utils.format_dt(
                                        ciso8601.parse_datetime(mainItem["start_date"])
                                    ),
                                    inline=True,
                                )
                                .add_field(
                                    name="End Date",
                                    value=discord.utils.format_dt(
                                        ciso8601.parse_datetime(mainItem["end_date"])
                                    ),
                                    inline=True,
                                )
                                .add_field(
                                    name="Timezone",
                                    value=mainItem["timezone"],
                                    inline=True,
                                )
                                .add_field(
                                    name="Week", value=mainItem["week"], inline=True
                                )
                                .add_field(
                                    name="Year", value=mainItem["year"], inline=True
                                )
                                for mainItem in dataMain2
                            ],
                            loop_pages=True,
                        )
                        await mainPages.respond(ctx.interaction, ephemeral=False)
                except NoItemsError:
                    embedError = discord.Embed()
                    embedError.description = "It seems like there are no teams named like that. Please try again"
                    await ctx.respond(embed=embedError)

    @blueAllianceMatches.command(name="team")
    async def blueAllianceTeamMatches(
        self,
        ctx,
        *,
        team_number: Option(int, "The FRC team number"),
        event_key: Option(str, "The event key"),
    ):
        """Testing for team matches"""
        try:
            async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
                headers = {"X-TBA-Auth-Key": API_KEY}
                async with session.get(
                    f"https://www.thebluealliance.com/api/v3/team/frc{team_number}/event/{event_key}/matches",
                    headers=headers,
                ) as r:
                    data = await r.content.read()
                    dataMain = parser.parse(data, recursive=True)
                    if "Error" in dataMain or len(dataMain) == 0:
                        raise NoItemsError
                    else:
                        pageGroupLists = [
                            pages.PageGroup(
                                pages=[
                                    discord.Embed(
                                        title=f"Match {items['match_number']}",
                                        description=str(
                                            items["alliances"]["blue"]["team_keys"]
                                        ).replace("'", ""),
                                        color=discord.Color.blue(),
                                    )
                                    .add_field(
                                        name="Total Teleop Points",
                                        value=items["score_breakdown"]["blue"][
                                            "teleopPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Total Endgame Points",
                                        value=items["score_breakdown"]["blue"][
                                            "endgamePoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Total Points",
                                        value=items["score_breakdown"]["blue"][
                                            "totalPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Foul Count",
                                        value=items["score_breakdown"]["blue"][
                                            "foulCount"
                                        ],
                                    )
                                    .add_field(
                                        name="Foul Points",
                                        value=items["score_breakdown"]["blue"][
                                            "foulPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Ranking Points",
                                        value=items["score_breakdown"]["blue"]["rp"],
                                    )
                                    for items in dataMain
                                ],
                                label="Blue Alliance",
                            ),
                            pages.PageGroup(
                                pages=[
                                    discord.Embed(
                                        title=f"Match {items['match_number']}",
                                        description=str(
                                            items["alliances"]["red"]["team_keys"]
                                        ).replace("'", ""),
                                        color=discord.Color.red(),
                                    )
                                    .add_field(
                                        name="Total Teleop Points",
                                        value=items["score_breakdown"]["red"][
                                            "teleopPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Total Endgame Points",
                                        value=items["score_breakdown"]["red"][
                                            "endgamePoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Total Points",
                                        value=items["score_breakdown"]["red"][
                                            "totalPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Foul Count",
                                        value=items["score_breakdown"]["red"][
                                            "foulCount"
                                        ],
                                    )
                                    .add_field(
                                        name="Foul Points",
                                        value=items["score_breakdown"]["red"][
                                            "foulPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Ranking Points",
                                        value=items["score_breakdown"]["red"]["rp"],
                                    )
                                    for items in dataMain
                                ],
                                label="Red Alliance",
                            ),
                        ]
                        mainPages = pages.Paginator(
                            pages=pageGroupLists, show_menu=True
                        )
                        await mainPages.respond(ctx.interaction)
        except NoItemsError:
            embedError = discord.Embed()
            embedError.description = "It seems like there are no teams and/or event keys named like that. Please try again"
            await ctx.respond(embed=embedError)

    @blueAlliance.command(name="rankings")
    async def blueAllianceEventRankings(
        self, ctx, *, frc_event_key: Option(str, "The event key")
    ):
        """Returns the event ranking"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {"X-TBA-Auth-Key": API_KEY}
            async with session.get(
                f"https://www.thebluealliance.com/api/v3/event/{frc_event_key}/rankings",
                headers=headers,
            ) as r:
                data = await r.content.read()
                dataMain = parser.parse(data, recursive=True)
                try:
                    mainPages = pages.Paginator(
                        pages=[
                            discord.Embed(
                                title=f'Rank {dictItem["rank"]} - {str(dictItem["team_key"]).replace("frc", "")}'
                            )
                            .add_field(name="Losses", value=dictItem["losses"])
                            .add_field(name="Ties", value=dictItem["ties"])
                            .add_field(name="Wins", value=dictItem["wins"])
                            for dictItem in dataMain["rankings"]
                        ],
                        loop_pages=True,
                    )
                    await mainPages.respond(ctx.interaction, ephemeral=False)
                except KeyError:
                    embedError = discord.Embed()
                    embedError.description = (
                        "It seems like there are no records available. Please try again"
                    )
                    await ctx.respond(embed=embedError)

    @blueAllianceMatches.command(name="all")
    async def blueAllianceEventMatches(
        self, ctx, *, frc_event_key: Option(str, "The event key")
    ):
        """Returns all of the matches for an FRC event"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {"X-TBA-Auth-Key": API_KEY}
            async with session.get(
                f"https://www.thebluealliance.com/api/v3/event/{frc_event_key}/matches",
                headers=headers,
            ) as r:
                data = await r.content.read()
                dataMain = parser.parse(data, recursive=True)
                try:
                    if "Error" in dataMain or len(dataMain) == 0:
                        raise NoItemsError
                    else:
                        pageGroupLists = [
                            pages.PageGroup(
                                pages=[
                                    discord.Embed(
                                        title=f"(Blue Alliance) Match {items['match_number']} - {items['comp_level']}",
                                        description=str(
                                            items["alliances"]["blue"]["team_keys"]
                                        ).replace("'", ""),
                                        color=discord.Color.blue(),
                                    )
                                    .add_field(
                                        name="Winning Alliance",
                                        value=items["winning_alliance"],
                                    )
                                    .add_field(
                                        name="Time",
                                        value=discord.utils.format_dt(
                                            datetime.utcfromtimestamp(items["time"])
                                        ),
                                    )
                                    .add_field(
                                        name="Video",
                                        value="None"
                                        if len(items["videos"]) == 0
                                        else [
                                            str(
                                                f"https://www.youtube.com/watch?v={item['key']}"
                                            ).replace("'", "")
                                            for item in items["videos"]
                                            if item["type"] == "youtube"
                                        ],
                                    )
                                    .add_field(
                                        name="Total Teleop Points",
                                        value=items["score_breakdown"]["blue"][
                                            "teleopPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Total Endgame Points",
                                        value=items["score_breakdown"]["blue"][
                                            "endgamePoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Total Points",
                                        value=items["score_breakdown"]["blue"][
                                            "totalPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Foul Count",
                                        value=items["score_breakdown"]["blue"][
                                            "foulCount"
                                        ],
                                    )
                                    .add_field(
                                        name="Foul Points",
                                        value=items["score_breakdown"]["blue"][
                                            "foulPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Ranking Points",
                                        value=items["score_breakdown"]["blue"]["rp"],
                                    )
                                    for items in dataMain
                                ],
                                label="Blue Alliance",
                            ),
                            pages.PageGroup(
                                pages=[
                                    discord.Embed(
                                        title=f"(Red Alliance) Match {items['match_number']} - {items['comp_level']}",
                                        description=str(
                                            items["alliances"]["red"]["team_keys"]
                                        ).replace("'", ""),
                                        color=discord.Color.red(),
                                    )
                                    .add_field(
                                        name="Winning Alliance",
                                        value=items["winning_alliance"],
                                    )
                                    .add_field(
                                        name="Time",
                                        value=discord.utils.format_dt(
                                            datetime.utcfromtimestamp(items["time"])
                                        ),
                                    )
                                    .add_field(
                                        name="Video",
                                        value="None"
                                        if len(items["videos"]) == 0
                                        else [
                                            str(
                                                f"https://www.youtube.com/watch?v={item['key']}"
                                            ).replace("'", "")
                                            for item in items["videos"]
                                            if item["type"] == "youtube"
                                        ],
                                    )
                                    .add_field(
                                        name="Total Teleop Points",
                                        value=items["score_breakdown"]["red"][
                                            "teleopPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Total Endgame Points",
                                        value=items["score_breakdown"]["red"][
                                            "endgamePoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Total Points",
                                        value=items["score_breakdown"]["red"][
                                            "totalPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Foul Count",
                                        value=items["score_breakdown"]["red"][
                                            "foulCount"
                                        ],
                                    )
                                    .add_field(
                                        name="Foul Points",
                                        value=items["score_breakdown"]["red"][
                                            "foulPoints"
                                        ],
                                    )
                                    .add_field(
                                        name="Ranking Points",
                                        value=items["score_breakdown"]["red"]["rp"],
                                    )
                                    for items in dataMain
                                ],
                                label="Red Alliance",
                            ),
                        ]
                        mainPages = pages.Paginator(
                            pages=pageGroupLists,
                            show_menu=True,
                            menu_placeholder="Choose Alliance",
                        )
                        await mainPages.respond(ctx.interaction)
                except NoItemsError:
                    embedError = discord.Embed()
                    embedError.description = (
                        "It seems like there are no records available. Please try again"
                    )
                    await ctx.respond(embed=embedError)


def setup(bot):
    bot.add_cog(BlueAlliance(bot))
