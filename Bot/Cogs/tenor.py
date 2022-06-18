import asyncio
import os

import aiohttp
import discord
import orjson
import simdjson
import uvloop
from discord.commands import Option, slash_command
from discord.ext import commands, pages
from dotenv import load_dotenv

load_dotenv()

Tenor_API_Key = os.getenv("Tenor_API_Key")
parser = simdjson.Parser()


class TenorV1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="tenor-search-multiple",
        description="Searches for up to 3 gifs on Tenor",
    )
    async def tenor_search(
        self, ctx, *, search_term: Option(str, "Search Term for GIFs")
    ):
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {
                "q": search_term,
                "key": Tenor_API_Key,
                "contentfilter": "medium",
                "limit": 3,
                "media_filter": "minimal",
            }
            async with session.get("https://g.tenor.com/v1/search", params=params) as r:
                data = await r.content.read()
                dataMain = parser.parse(data, recursive=True)
                try:
                    try:
                        if len(dataMain["results"]) == 0:
                            raise ValueError
                        else:
                            mainPages = pages.Paginator(
                                pages=[
                                    discord.Embed(
                                        title=dictItem["content_description"]
                                    ).set_image(
                                        url=str(
                                            [
                                                item["gif"]["url"]
                                                for item in dictItem.get("media")
                                            ]
                                        )
                                        .replace("[", "")
                                        .replace("]", "")
                                        .replace("'", "")
                                    )
                                    for dictItem in dataMain["results"]
                                ],
                                loop_pages=True,
                            )
                            await mainPages.respond(ctx.interaction, ephemeral=False)
                    except ValueError:
                        embedNoItemsError = discord.Embed()
                        embedNoItemsError.description = (
                            "No GIFs found for that search term"
                        )
                        await ctx.respond(embed=embedNoItemsError)
                except Exception as e:
                    embedVar = discord.Embed()
                    embedVar.description = f"Sorry, but the search for {search_term} has failed. Please try again..."
                    embedVar.add_field(name="Reason", value=e, inline=True)
                    await ctx.respond(embed=embedVar)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class TenorV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="tenor-search-one",
        description="Searches for a single gif on Tenor",
    )
    async def tenor_search_one(
        self, ctx, *, search_one_term: Option(str, "Search Term for GIF")
    ):
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {
                "q": search_one_term,
                "key": Tenor_API_Key,
                "contentfilter": "medium",
                "limit": 1,
                "media_filter": "minimal",
            }
            async with session.get(
                "https://g.tenor.com/v1/search", params=params
            ) as re:
                data2 = await re.content.read()
                dataMain2 = parser.parse(data2, recursive=True)
                try:
                    try:
                        if len(dataMain2["results"]) == 0:
                            raise ValueError
                        else:
                            embedPages = pages.Paginator(
                                pages=[
                                    discord.Embed(
                                        title=dictItem["content_description"]
                                    ).set_image(
                                        url=str(
                                            [
                                                item["gif"]["url"]
                                                for item in dictItem.get("media")
                                            ]
                                        )
                                        .replace("[", "")
                                        .replace("]", "")
                                        .replace("'", "")
                                    )
                                    for dictItem in dataMain2["results"]
                                ],
                                loop_pages=True,
                            )
                            await embedPages.respond(ctx.interaction, ephemeral=False)
                    except ValueError:
                        embedNoItemsError = discord.Embed()
                        embedNoItemsError.description = (
                            "No GIFs found for that search term"
                        )
                        await ctx.respond(embed=embedNoItemsError)
                except Exception as e:
                    embedVar = discord.Embed()
                    embedVar.description = f"Sorry, but the search for {search_one_term} has failed. Please try again..."
                    embedVar.add_field(name="Reason", value=e, inline=True)
                    await ctx.respond(embed=embedVar)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class TenorV3(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="tenor-trending",
        description="Returns up to 3 trending gifs from Tenor",
    )
    async def tenor_trending(self, ctx):
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {
                "key": Tenor_API_Key,
                "contentfilter": "medium",
                "limit": 3,
                "media_filter": "minimal",
            }
            async with session.get(
                "https://g.tenor.com/v1/trending", params=params
            ) as response:
                data3 = await response.content.read()
                dataMain3 = parser.parse(data3, recursive=True)
                try:
                    try:
                        if len(dataMain3["results"]) == 0:
                            raise ValueError
                        else:
                            embedPages = pages.Paginator(
                                pages=[
                                    discord.Embed(
                                        title=dictItem2["content_description"]
                                    ).set_image(
                                        url=str(
                                            [
                                                item["gif"]["url"]
                                                for item in dictItem2.get("media")
                                            ]
                                        )
                                        .replace("[", "")
                                        .replace("]", "")
                                        .replace("'", "")
                                    )
                                    for dictItem2 in dataMain3["results"]
                                ],
                                loop_pages=True,
                            )
                            await embedPages.respond(ctx.interaction, ephemeral=False)
                    except ValueError:
                        embedNoItemsError = discord.Embed()
                        embedNoItemsError.description = (
                            "Apparently there are no trending gifs... werid huh"
                        )
                        await ctx.respond(embed=embedNoItemsError)
                except Exception as e:
                    embedVar = discord.Embed()
                    embedVar.description = (
                        "Sorry, but the query has failed. Please try again..."
                    )
                    embedVar.add_field(name="Reason", value=e, inline=True)
                    await ctx.respond(embed=embedVar)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class TenorV4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="tenor-search-suggestions",
        description="Gives a list of suggested search terms based on given topic",
    )
    async def tenor_search_suggestions(
        self,
        ctx,
        *,
        search_suggestion: Option(str, "Topic/Search Term for Search Suggestion"),
    ):
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {"key": Tenor_API_Key,
                      "q": search_suggestion, "limit": 25}
            async with session.get(
                "https://g.tenor.com/v1/search_suggestions", params=params
            ) as resp:
                data5 = await resp.content.read()
                dataMain5 = parser.parse(data5, recursive=True)
                try:
                    try:
                        if len(dataMain5["results"]) == 0:
                            raise ValueError
                        else:
                            embedVar = discord.Embed()
                            embedVar.title = "Search Suggestions"
                            embedVar.description = str(
                                [items for items in dataMain5["results"]]
                            ).replace("'", "")
                            await ctx.respond(embed=embedVar)
                    except ValueError:
                        embedNoItemsError = discord.Embed()
                        embedNoItemsError.description = (
                            "Apparently there are no terms... werid huh"
                        )
                        await ctx.respond(embed=embedNoItemsError)
                except Exception as e:
                    embedVar = discord.Embed()
                    embedVar.description = f"Sorry, but the search for {search_suggestion} has failed. Please try again..."
                    embedVar.add_field(name="Reason", value=e, inline=True)
                    await ctx.respond(embed=embedVar)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class TenorV5(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="tenor-trending-terms",
        description="Gives a list of trending search terms on Tenor",
    )
    async def tenor_trending_terms(self, ctx):
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {"key": Tenor_API_Key, "limit": 25}
            async with session.get(
                "https://g.tenor.com/v1/trending_terms", params=params
            ) as rep:
                data6 = await rep.content.read()
                dataMain6 = parser.parse(data6, recursive=True)
                try:
                    try:
                        if len(dataMain6["results"]) == 0:
                            raise ValueError
                        else:
                            embedVar = discord.Embed()
                            embedVar.title = "Trending Search Terms"
                            embedVar.description = str(
                                [items for items in dataMain6["results"]]
                            ).replace("'", "")
                            await ctx.respond(embed=embedVar)
                    except ValueError:
                        embedNoItemsError = discord.Embed()
                        embedNoItemsError.description = (
                            "Apparently there are no trending terms... werid huh"
                        )
                        await ctx.respond(embed=embedNoItemsError)
                except Exception as e:
                    embedVar = discord.Embed()
                    embedVar.description = "Sorry, but the search for {search} has failed. Please try again..."
                    embedVar.add_field(name="Reason", value=e, inline=True)
                    await ctx.respond(embed=embedVar)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class TenorV6(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="tenor-gif",
        description="Gives a gif based on the given GIF ID",
    )
    async def tenor_gif(self, ctx, *, search_gif: Option(int, "Tenor GIF ID")):
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {
                "key": Tenor_API_Key,
                "ids": search_gif,
                "limit": 1,
                "media_filter": "minimal",
            }
            async with session.get(
                "https://g.tenor.com/v1/gifs", params=params
            ) as respon:
                data7 = await respon.content.read()
                dataMain7 = parser.parse(data7, recursive=True)
                embedVar = discord.Embed()
                filterList2 = [
                    "created",
                    "bg_color",
                    "content_rating",
                    "title",
                    "h1_title",
                    "url",
                    "hasaudio",
                    "hascaption",
                    "source_id",
                    "composite",
                    "media",
                    "tags",
                    "flags",
                    "content_description",
                    "shares",
                ]
                try:
                    try:
                        if len(dataMain7["results"]) == 0:
                            raise ValueError
                        for dictValues in dataMain7["results"]:
                            for k, v in dictValues.items():
                                if k not in filterList2:
                                    embedVar.title = dictValues["content_description"]
                                    embedVar.add_field(
                                        name=str(k).capitalize(), value=v, inline=True
                                    )
                            for item3 in dictValues.get("media"):
                                embedVar.set_image(url=item3["gif"]["url"])
                            await ctx.respond(embed=embedVar)
                    except ValueError:
                        embedNoItemsError = discord.Embed()
                        embedNoItemsError.description = (
                            "It seems like that gif doesn't exist... Please try again"
                        )
                        await ctx.respond(embed=embedNoItemsError)
                except Exception as e:
                    embedError = discord.Embed()
                    embedError.description = (
                        "Sorry, but the query failed. Please try again..."
                    )
                    embedError.add_field(name="Reason", value=e, inline=True)
                    await ctx.respond(embed=embedError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class TenorV7(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="tenor-random",
        description="Gives 3 random gif from Tenor based on given search term",
    )
    async def tenor_random(
        self, ctx, *, search_random_term: Option(str, "Search Term")
    ):
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {
                "key": Tenor_API_Key,
                "limit": 3,
                "media_filter": "minimal",
                "contentfilter": "medium",
                "q": search_random_term,
            }
            async with session.get(
                "https://g.tenor.com/v1/random", params=params
            ) as object3:
                data8 = await object3.content.read()
                dataMain8 = parser.parse(data8, recursive=True)
                try:
                    try:
                        if len(dataMain8["results"]) == 0:
                            raise ValueError
                        else:
                            embedVar = discord.Embed()
                            moreEmbedPages = pages.Paginator(
                                pages=[
                                    discord.Embed(
                                        title=dictItem["content_description"]
                                    ).set_image(
                                        url=str(
                                            [
                                                item["gif"]["url"]
                                                for item in dictItem.get("media")
                                            ]
                                        )
                                        .replace("[", "")
                                        .replace("]", "")
                                        .replace("'", "")
                                    )
                                    for dictItem in dataMain8["results"]
                                ],
                                loop_pages=True,
                            )
                            await moreEmbedPages.respond(
                                ctx.interaction, ephemeral=False
                            )
                    except ValueError:
                        embedNoItemsError = discord.Embed()
                        embedNoItemsError.description = (
                            "Apparently there are no gifs..."
                        )
                        await ctx.respond(embed=embedNoItemsError)
                except Exception as e:
                    embedVar = discord.Embed()
                    embedVar.description = (
                        "Sorry, but the query failed. Please try again..."
                    )
                    embedVar.add_field(name="Reason", value=e, inline=True)
                    await ctx.respond(embed=embedVar)


    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def setup(bot):
    bot.add_cog(TenorV1(bot))
    bot.add_cog(TenorV2(bot))
    bot.add_cog(TenorV3(bot))
    bot.add_cog(TenorV4(bot))
    bot.add_cog(TenorV5(bot))
    # bot.add_cog(TenorV6(bot))
    bot.add_cog(TenorV7(bot))
