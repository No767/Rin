import asyncio

import discord
import uvloop
from discord.commands import Option, slash_command
from discord.ext import commands, pages
from rin_exceptions import NoItemsError
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

class AniListV1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="anilist-anime", description="Searches for up to 25 animes on AniList")
    async def aniListSearchAnime(
        self, ctx, *, anime_name: Option(str, "The name of the anime")
    ):
        transport = AIOHTTPTransport(url="https://graphql.anilist.co/")
        async with Client(
            transport=transport,
            fetch_schema_from_transport=True,
        ) as session:
            query = gql(
                """
            query ($animeName: String!, $perPage: Int, $isAdult: Boolean!) {
                Page (perPage: $perPage){
                    media(search: $animeName, isAdult: $isAdult, type: ANIME) {
                        title {
                            native
                            english
                            romaji
                        }
                        description
                        format
                        status
                        seasonYear
                        startDate {
                            day
                            month
                            year
                        }
                        endDate {
                            day
                            month
                            year
                        }
                        coverImage {
                            extraLarge
                        }
                        genres
                        tags {
                            name
                        }
                        synonyms
                        
                    }
                }
            }
        """
            )

            params = {"animeName": anime_name, "perPage": 25, "isAdult": False}
            data = await session.execute(query, variable_values=params)
            try:
                if len(data["Page"]["media"]) == 0:
                    raise NoItemsError
                else:
                    mainPages = pages.Paginator(
                        pages=[
                            discord.Embed(
                                title=mainItem["title"]["romaji"],
                                description=str(mainItem["description"]).replace(
                                    "<br>", ""
                                ),
                            )
                            .add_field(
                                name="Native Name",
                                value=f'[{mainItem["title"]["native"]}]',
                                inline=True,
                            )
                            .add_field(
                                name="English Name",
                                value=f'[{mainItem["title"]["english"]}]',
                                inline=True,
                            )
                            .add_field(
                                name="Status", value=mainItem["status"], inline=True
                            )
                            .add_field(
                                name="Start Date",
                                value=f'{mainItem["startDate"]["year"]}-{mainItem["startDate"]["month"]}-{mainItem["startDate"]["day"]}',
                                inline=True,
                            )
                            .add_field(
                                name="End Date",
                                value=f'{mainItem["endDate"]["year"]}-{mainItem["endDate"]["month"]}-{mainItem["endDate"]["day"]}',
                                inline=True,
                            )
                            .add_field(
                                name="Genres", value=mainItem["genres"], inline=True
                            )
                            .add_field(
                                name="Synonyms", value=mainItem["synonyms"], inline=True
                            )
                            .add_field(
                                name="Format", value=mainItem["format"], inline=True
                            )
                            .add_field(
                                name="Season Year",
                                value=mainItem["seasonYear"],
                                inline=True,
                            )
                            .add_field(
                                name="Tags",
                                value=[tagItem["name"] for tagItem in mainItem["tags"]],
                                inline=True,
                            )
                            .set_image(url=mainItem["coverImage"]["extraLarge"])
                            for mainItem in data["Page"]["media"]
                        ],
                        loop_pages=True,
                    )
                    await mainPages.respond(ctx.interaction, ephemeral=False)
            except NoItemsError:
                embedNoItemsError = discord.Embed()
                embedNoItemsError.description = "Sorry, but there seems to be no anime(s) with that name. Please try again"
                await ctx.respond(embed=embedNoItemsError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class AniListV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @slash_command(name="anilist-manga", description="Searches for up to 25 mangas on AniList")
    async def aniListSearchManga(
        self, ctx, *, manga_name: Option(str, "The name of the manga")
    ):
        transport = AIOHTTPTransport(url="https://graphql.anilist.co/")
        async with Client(
            transport=transport,
            fetch_schema_from_transport=True,
        ) as session:
            query = gql(
                """
            query ($mangaName: String!, $perPage: Int, $isAdult: Boolean!) {
                Page (perPage: $perPage){
                    media(search: $mangaName, isAdult: $isAdult, type: MANGA) {
                        title {
                            native
                            english
                            romaji
                        }
                        description
                        format
                        status
                        startDate {
                            day
                            month
                            year
                        }
                        endDate {
                            day
                            month
                            year
                        }
                        coverImage {
                            extraLarge
                        }
                        genres
                        tags {
                            name
                        }
                        synonyms
                        
                    }
                }
            }
        """
            )

            params = {"mangaName": manga_name, "perPage": 25, "isAdult": False}
            data = await session.execute(query, variable_values=params)
            try:
                if len(data["Page"]["media"]) == 0:
                    raise NoItemsError
                else:
                    mainPages2 = pages.Paginator(
                        pages=[
                            discord.Embed(
                                title=mainItem["title"]["romaji"],
                                description=str(mainItem["description"]).replace(
                                    "<br>", ""
                                ),
                            )
                            .add_field(
                                name="Native Name",
                                value=f'[{mainItem["title"]["native"]}]',
                                inline=True,
                            )
                            .add_field(
                                name="English Name",
                                value=f'[{mainItem["title"]["english"]}]',
                                inline=True,
                            )
                            .add_field(
                                name="Status", value=mainItem["status"], inline=True
                            )
                            .add_field(
                                name="Start Date",
                                value=f'{mainItem["startDate"]["year"]}-{mainItem["startDate"]["month"]}-{mainItem["startDate"]["day"]}',
                                inline=True,
                            )
                            .add_field(
                                name="End Date",
                                value=f'{mainItem["endDate"]["year"]}-{mainItem["endDate"]["month"]}-{mainItem["endDate"]["day"]}',
                                inline=True,
                            )
                            .add_field(
                                name="Genres", value=mainItem["genres"], inline=True
                            )
                            .add_field(
                                name="Synonyms", value=mainItem["synonyms"], inline=True
                            )
                            .add_field(
                                name="Format", value=mainItem["format"], inline=True
                            )
                            .add_field(
                                name="Tags",
                                value=[tagItem["name"] for tagItem in mainItem["tags"]],
                                inline=True,
                            )
                            .set_image(url=mainItem["coverImage"]["extraLarge"])
                            for mainItem in data["Page"]["media"]
                        ],
                        loop_pages=True,
                    )

                    await mainPages2.respond(ctx.interaction, ephemeral=False)
            except NoItemsError:
                embedNoItemsError = discord.Embed()
                embedNoItemsError.description = "Sorry, but there seems to be no manga(s) with that name. Please try again"
                await ctx.respond(embed=embedNoItemsError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class AniListV3(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name="anilist-tags", description="Searches for up to 25 tags on AniList") 
    async def aniListSearchTags(
        self, ctx, *, tags: Option(str, "The name of the tag to search for")
    ):
        transport = AIOHTTPTransport(url="https://graphql.anilist.co/")
        async with Client(
            transport=transport,
            fetch_schema_from_transport=True,
        ) as session:
            query = gql(
                """
            query ($tagName: String!, $perPage: Int, $isAdult: Boolean!) {
                Page (perPage: $perPage){
                    media(tag: $tagName, isAdult: $isAdult) {
                        title {
                            native
                            english
                            romaji
                        }
                        description
                        format
                        status
                        startDate {
                            day
                            month
                            year
                        }
                        endDate {
                            day
                            month
                            year
                        }
                        coverImage {
                            extraLarge
                        }
                        genres
                        type
                        tags {
                            name
                        }
                        synonyms
                        
                    }
                }
            }
        """
            )

            params = {"tagName": tags, "perPage": 25, "isAdult": False}
            data = await session.execute(query, variable_values=params)
            try:
                if len(data["Page"]["media"]) == 0:
                    raise NoItemsError
                else:
                    mainPages2 = pages.Paginator(
                        pages=[
                            discord.Embed(
                                title=mainItem["title"]["romaji"],
                                description=str(mainItem["description"]).replace(
                                    "<br>", ""
                                ),
                            )
                            .add_field(
                                name="Native Name",
                                value=f'[{mainItem["title"]["native"]}]',
                                inline=True,
                            )
                            .add_field(
                                name="English Name",
                                value=f'[{mainItem["title"]["english"]}]',
                                inline=True,
                            )
                            .add_field(
                                name="Status", value=mainItem["status"], inline=True
                            )
                            .add_field(
                                name="Start Date",
                                value=f'{mainItem["startDate"]["year"]}-{mainItem["startDate"]["month"]}-{mainItem["startDate"]["day"]}',
                                inline=True,
                            )
                            .add_field(
                                name="End Date",
                                value=f'{mainItem["endDate"]["year"]}-{mainItem["endDate"]["month"]}-{mainItem["endDate"]["day"]}',
                                inline=True,
                            )
                            .add_field(
                                name="Genres", value=mainItem["genres"], inline=True
                            )
                            .add_field(
                                name="Synonyms", value=mainItem["synonyms"], inline=True
                            )
                            .add_field(
                                name="Format", value=mainItem["format"], inline=True
                            )
                            .add_field(name="Type", value=mainItem["type"], inline=True)
                            .add_field(
                                name="Tags",
                                value=[tagItem["name"] for tagItem in mainItem["tags"]],
                                inline=True,
                            )
                            .set_image(url=mainItem["coverImage"]["extraLarge"])
                            for mainItem in data["Page"]["media"]
                        ],
                        loop_pages=True,
                    )

                    await mainPages2.respond(ctx.interaction, ephemeral=False)
            except NoItemsError:
                embedNoItemsError = discord.Embed()
                embedNoItemsError.description = "Sorry, but there seems to be no tag with that name. Please try again"
                await ctx.respond(embed=embedNoItemsError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class AniListV4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @slash_command(name="anilist-characters", description="Searches for up to 25 characters on AniList")
    async def aniListSearchCharacter(
        self, ctx, *, anime_character: Option(str, "The character to search for")
    ):
        transport = AIOHTTPTransport(url="https://graphql.anilist.co/")
        async with Client(
            transport=transport,
            fetch_schema_from_transport=True,
        ) as session:
            mainQuery = gql(
                """ 
                query ($search: String!, $perPage: Int) {
                    Page (perPage: $perPage) {
                        characters (search: $search) {
                            name {
                                full
                                native
                                alternative
                            }
                            description
                            image {
                                large
                            }
                            gender
                            age
                            media {
                                nodes {
                                    title {
                                        romaji
                                    }
                                }
                            }

                        }
                    }
                }
                """
            )
            params = {"search": anime_character, "perPage": 25}
            data = await session.execute(mainQuery, variable_values=params)
            try:
                if len(data["Page"]["characters"]) == 0:
                    raise NoItemsError
                else:
                    print(data)
                    pagesMain2 = pages.Paginator(
                        pages=[
                            discord.Embed(
                                title=f'{mainItem3["name"]["full"]} - {mainItem3["name"]["native"]}',
                                description=mainItem3["description"],
                            )
                            .add_field(
                                name="Alternative Name",
                                value=str(mainItem3["name"]["alternative"]).replace(
                                    "'", ""
                                ),
                                inline=True,
                            )
                            .add_field(
                                name="Gender", value=mainItem3["gender"], inline=True
                            )
                            .add_field(name="Age", value=mainItem3["age"], inline=True)
                            .add_field(
                                name="Media",
                                value=str(
                                    [
                                        mediaMain["title"]["romaji"]
                                        for mediaMain in mainItem3["media"]["nodes"]
                                    ]
                                ).replace("'", ""),
                            )
                            .set_image(url=mainItem3["image"]["large"])
                            for mainItem3 in data["Page"]["characters"]
                        ],
                        loop_pages=True,
                    )
                    await pagesMain2.respond(ctx.interaction, ephemeral=False)
            except NoItemsError:
                embedNoItemsError = discord.Embed()
                embedNoItemsError.description = "Sorry, but there seems to be no anime and/or manga characters with that name. Please try again"
                await ctx.respond(embed=embedNoItemsError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def setup(bot):
    bot.add_cog(AniListV1(bot))
    bot.add_cog(AniListV2(bot))
    bot.add_cog(AniListV3(bot))
    bot.add_cog(AniListV4(bot))