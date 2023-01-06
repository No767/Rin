import asyncio
from typing import Dict, List

import aiohttp
import ciso8601
import discord
import orjson
import simdjson
import uvloop
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands, pages
from rin_exceptions import NoItemsError

jsonParser = simdjson.Parser()


class List(list):
    def __setitem__(self, id, data):
        super().__setitem__(id - 1, data)

    def __getitem__(self, id):
        return super().__getitem__(id - 1)


def formatMangaTitles(titles: Dict) -> List:
    return titles["en"] if "en" in titles else [v for _, v in titles.items()]


def formatAltTitles(titles: List) -> List:
    for items in titles:
        if "en" in items:
            return [items["en"]]
        else:
            return [v for _, v in items.items()]


def formatMangaDescriptions(descriptions: Dict) -> List:
    return (
        descriptions["en"]
        if "en" in descriptions
        else [v for _, v in descriptions["description"].items()]
    )


def formatTags(tags: Dict) -> List:
    return (
        tags["en"]
        if "en" in tags
        else ", ".join([v for _, v in tags["name"].items()]).rstrip(", ")
    )


class ChapterSelection(discord.ui.Select):
    def __init__(self, chapters: List):
        super().__init__(
            placeholder="Choose a chapter",
            options=[
                discord.SelectOption(
                    select_type=discord.ComponentType.string_select,
                    label=f"Chapter {items['chapter']} - {items['title']}",
                )
                for items in chapters
            ],
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("FREEDOM!!!")


class SelectMangaRead(discord.ui.View):
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

    def __init__(self, mangaData: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mangaData = mangaData

    @discord.ui.button(
        label="Select",
        row=1,
        style=discord.ButtonStyle.primary,
        emoji=discord.PartialEmoji.from_str("<:check:314349398811475968>"),
    )
    async def callback(self, button, interaction: discord.Interaction) -> None:
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {
                "contentRating[]": ["safe"],
                "translatedLanguage[]": ["en"],
                "order[createdAt]": "asc",
            }
            mangaID = self.mangaData["id"]
            async with session.get(
                f"https://api.mangadex.org/manga/{mangaID}/feed", params=params
            ) as r:
                data = await r.content.read()
                dataMain = jsonParser.parse(data, recursive=True)
                newDict = sorted(
                    [
                        {
                            "id": item["id"],
                            "chapter": item["attributes"]["chapter"],
                            "title": item["attributes"]["title"],
                            "volume": item["attributes"]["volume"],
                        }
                        for item in dataMain["data"]
                    ],
                    key=lambda x: x["chapter"],
                )
                await interaction.response.edit_message(
                    "Please select a given chapter",
                    view=discord.ui.View(ChapterSelection(chapters=newDict)),
                )


class MangaDex(commands.Cog):
    """Commands for getting data from MangaDex"""

    def __init__(self, bot):
        self.bot = bot

    md = SlashCommandGroup(
        "mangadex", "Commmands for the MangaDex service", guild_ids=[866199405090308116]
    )
    mdSearch = md.create_subgroup(
        "search", "Search for stuff on MangaDex", guild_ids=[866199405090308116]
    )
    mdScanlation = md.create_subgroup(
        "scanlation", "Commands for the scanlation section"
    )

    @mdSearch.command(name="manga")
    async def relatedManga(self, ctx, name: Option(str, "Name of manga")):
        """Search for manga on MangaDex"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {
                "title": name,
                "publicationDemographic[]": "none",
                "contentRating[]": "safe",
                "order[title]": "asc",
                "limit": 25,
                "includes[]": ["cover_art", "manga", "tags", "author"],
            }
            async with session.get(
                f"https://api.mangadex.org/manga/", params=params
            ) as r:
                data = await r.content.read()
                dataMain = jsonParser.parse(data, recursive=True)
                try:
                    mainPageGroups = [
                        pages.PageGroup(
                            pages=[
                                discord.Embed(
                                    title=formatMangaTitles(
                                        items["attributes"]["title"]
                                    ),
                                    description=formatMangaDescriptions(
                                        items["attributes"]["description"]
                                    ),
                                )
                                .add_field(
                                    name="Alt Titles",
                                    value=formatAltTitles(
                                        items["attributes"]["altTitles"]
                                    ),
                                )
                                .add_field(
                                    name="Tags",
                                    value=[
                                        formatTags(tags["attributes"]["name"])
                                        for tags in items["attributes"]["tags"]
                                    ],
                                )
                                .add_field(
                                    name="Status", value=items["attributes"]["status"]
                                )
                                .add_field(
                                    name="Year", value=items["attributes"]["year"]
                                )
                                .add_field(
                                    name="Created At",
                                    value=discord.utils.format_dt(
                                        ciso8601.parse_datetime(
                                            items["attributes"]["createdAt"]
                                        )
                                    ),
                                )
                                .add_field(
                                    name="Updated At",
                                    value=discord.utils.format_dt(
                                        ciso8601.parse_datetime(
                                            items["attributes"]["updatedAt"]
                                        )
                                    ),
                                )
                                .set_image(
                                    url=[
                                        f'https://uploads.mangadex.org/covers/{items["id"]}/{subItems["attributes"]["fileName"]}'
                                        for subItems in items["relationships"]
                                        if subItems["type"] == "cover_art"
                                    ][0]
                                )
                                for items in dataMain["data"]
                            ],
                            label="Manga",
                            description="View the results of your search",
                        ),
                        pages.PageGroup(
                            pages=[
                                [
                                    discord.Embed(
                                        title=formatMangaTitles(
                                            subItems["attributes"]["title"]
                                        ),
                                        description=formatMangaDescriptions(
                                            subItems["attributes"]["description"]
                                        ),
                                    )
                                    .add_field(
                                        name="Alt Titles",
                                        value=", ".join(
                                            formatAltTitles(
                                                subItems["attributes"]["altTitles"]
                                            )
                                        ),
                                    )
                                    .add_field(
                                        name="Tags",
                                        value=[
                                            formatTags(tags["attributes"]["name"])
                                            for tags in subItems["attributes"]["tags"]
                                        ],
                                    )
                                    .add_field(
                                        name="Status",
                                        value=subItems["attributes"]["status"],
                                    )
                                    .add_field(
                                        name="MangaDex URL",
                                        value=f"https://mangadex.org/title/{items['id']}",
                                    )
                                    .add_field(
                                        name="Created At",
                                        value=discord.utils.format_dt(
                                            ciso8601.parse_datetime(
                                                subItems["attributes"]["createdAt"]
                                            )
                                        ),
                                    )
                                    .add_field(
                                        name="Updated At",
                                        value=discord.utils.format_dt(
                                            ciso8601.parse_datetime(
                                                subItems["attributes"]["updatedAt"]
                                            )
                                        ),
                                    )
                                    for subItems in items["relationships"]
                                    if subItems["type"] == "manga"
                                ][:3]
                                for items in dataMain["data"]
                            ],
                            label="Related Manga",
                            description="View related manga",
                        ),
                        pages.PageGroup(
                            pages=[
                                [
                                    discord.Embed(
                                        title=subItems["attributes"]["name"],
                                        description=subItems["attributes"]["biography"],
                                    )
                                    .add_field(
                                        name="Twitter",
                                        value=subItems["attributes"]["twitter"]
                                        if subItems["attributes"]["twitter"] is not None
                                        else "None",
                                    )
                                    .add_field(
                                        name="Pixiv",
                                        value=subItems["attributes"]["pixiv"]
                                        if subItems["attributes"]["pixiv"] is not None
                                        else "None",
                                    )
                                    .add_field(
                                        name="YouTube",
                                        value=subItems["attributes"]["youtube"]
                                        if subItems["attributes"]["youtube"] is not None
                                        else "None",
                                    )
                                    for subItems in items["relationships"]
                                    if subItems["type"] == "author"
                                ]
                                for items in dataMain["data"]
                            ],
                            label="Author",
                            description="View the author of the manga(s)",
                        ),
                    ]
                    mainPages = pages.Paginator(pages=mainPageGroups, show_menu=True)
                    await mainPages.respond(ctx.interaction, ephemeral=False)
                except NoItemsError:
                    embedErrorAlt2 = discord.Embed()
                    embedErrorAlt2.description = "Sorry, but the manga you searched for does not exist or is invalid. Please try again."
                    await ctx.respond(embed=embedErrorAlt2)

    @md.command(name="random")
    async def manga_random(self, ctx):
        """Returns an random manga from MangaDex"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            async with session.get("https://api.mangadex.org/manga/random") as r:
                data2 = await r.content.read()
                dataMain2 = jsonParser.parse(data2, recursive=True)
                mangaFilter2 = [
                    "tags",
                    "title",
                    "altTitles",
                    "description",
                    "links",
                    "background",
                    "createdAt",
                    "updatedAt",
                ]
                tagFilter = ["id", "type", "relationships"]
                embedVar = discord.Embed()
                try:
                    try:
                        if r.status == 500:
                            embedErrorMain = discord.Embed()
                            embedErrorMain.description = "It seems like there is no manga to select from... Don't worry about it, just try again"
                            embedErrorMain.add_field(
                                name="HTTP Response Code", value=r.status, inline=True
                            )
                            await ctx.respond(embed=embedErrorMain)
                        elif len(dataMain2["data"]) == 0:
                            raise ValueError
                        else:
                            mangaTitle2 = (
                                dataMain2["data"]["attributes"]["title"]["en"]
                                if "en" in dataMain2["data"]["attributes"]["title"]
                                else dataMain2["data"]["attributes"]["title"]
                            )
                            mainDesc2 = (
                                dataMain2["data"]["attributes"]["description"]["en"]
                                if "en"
                                in dataMain2["data"]["attributes"]["description"]
                                else dataMain2["data"]["attributes"]["description"]
                            )
                            for k, v in dataMain2["data"]["attributes"].items():
                                if k not in mangaFilter2:
                                    embedVar.add_field(
                                        name=k, value=f"[{v}]", inline=True
                                    )
                            for tagItem in dataMain2["data"]["attributes"]["tags"]:
                                mainTags = [
                                    v["name"]["en"]
                                    for k, v in tagItem.items()
                                    if k not in tagFilter
                                ]
                            for item in dataMain2["data"]["relationships"]:
                                mangaID2 = dataMain2["data"]["id"]
                                if item["type"] not in ["manga", "author", "artist"]:
                                    coverArtID2 = item["id"]
                                    async with session.get(
                                        f"https://api.mangadex.org/cover/{coverArtID2}"
                                    ) as rp:
                                        cover_art_data2 = await rp.json(
                                            loads=orjson.loads
                                        )
                                        cover_art2 = cover_art_data2["data"][
                                            "attributes"
                                        ]["fileName"]
                                        embedVar.set_image(
                                            url=f"https://uploads.mangadex.org/covers/{mangaID2}/{cover_art2}"
                                        )
                            embedVar.title = (
                                str(mangaTitle2)
                                .replace("'", "")
                                .replace("[", "")
                                .replace("]", "")
                            )
                            embedVar.description = (
                                str(mainDesc2)
                                .replace("'", "")
                                .replace("[", "")
                                .replace("]", "")
                            )
                            embedVar.add_field(
                                name="Alt Titles",
                                value=str(
                                    [
                                        v
                                        for items in dataMain2["data"]["attributes"][
                                            "altTitles"
                                        ]
                                        for k, v in items.items()
                                    ]
                                ).replace("'", ""),
                                inline=True,
                            )
                            embedVar.add_field(
                                name="Tags",
                                value=str(mainTags).replace("'", ""),
                                inline=True,
                            )
                            embedVar.add_field(
                                name="MangaDex URL",
                                value=f'https://mangadex.org/title/{dataMain2["data"]["id"]}',
                                inline=True,
                            )
                            await ctx.respond(embed=embedVar)
                    except ValueError:
                        embedValErrorMain = discord.Embed()
                        embedValErrorMain.description = "It seems like there wasn't any manga found. Please try again"
                        await ctx.respond(embed=embedValErrorMain)
                except Exception as e:
                    embedErrorMain = discord.Embed()
                    embedErrorMain.description = "There was an error. Please try again."
                    embedErrorMain.add_field(name="Error", value=e, inline=True)
                    await ctx.respond(embed=embedErrorMain)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @mdSearch.command(name="scanlation")
    async def scanlation_search(
        self, ctx, *, name: Option(str, "The name of the scanlation group")
    ):
        """Returns up to 25 scanlation groups via the name given"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {
                "limit": 25,
                "name": name,
                "order[name]": "asc",
                "order[relevance]": "desc",
            }
            async with session.get(
                "https://api.mangadex.org/group", params=params
            ) as totally_another_response:
                md_data2 = await totally_another_response.content.read()
                mdDataMain = jsonParser.parse(md_data2, recursive=True)
                try:
                    if len(mdDataMain["data"]) == 0:
                        raise NoItemsError
                    else:
                        mainPages = pages.Paginator(
                            pages=[
                                discord.Embed(
                                    title=mainItem["attributes"]["name"],
                                    description=mainItem["attributes"]["description"],
                                )
                                .add_field(
                                    name="Alt Names",
                                    value=mainItem["attributes"]["altNames"],
                                    inline=True,
                                )
                                .add_field(
                                    name="Website",
                                    value=mainItem["attributes"]["website"],
                                    inline=True,
                                )
                                .add_field(
                                    name="Discord",
                                    value=f'https://discord.gg/{mainItem["attributes"]["discord"]}'
                                    if mainItem["attributes"]["discord"] is not None
                                    else "None",
                                    inline=True,
                                )
                                .add_field(
                                    name="Twitter",
                                    value=f'https://twitter.com/{mainItem["attributes"]["twitter"]}'
                                    if mainItem["attributes"]["twitter"] is not None
                                    else "None",
                                    inline=True,
                                )
                                .add_field(
                                    name="Contact Email",
                                    value=mainItem["attributes"]["contactEmail"],
                                    inline=True,
                                )
                                .add_field(
                                    name="Created At",
                                    value=discord.utils.format_dt(
                                        ciso8601.parse_datetime(
                                            mainItem["attributes"]["createdAt"]
                                        )
                                    ),
                                    inline=True,
                                )
                                .add_field(
                                    name="Updated At",
                                    value=discord.utils.format_dt(
                                        ciso8601.parse_datetime(
                                            mainItem["attributes"]["updatedAt"]
                                        )
                                    ),
                                    inline=True,
                                )
                                for mainItem in mdDataMain["data"]
                            ],
                            loop_pages=True,
                        )
                        await mainPages.respond(ctx.interaction, ephemeral=False)
                except NoItemsError:
                    embed1 = discord.Embed()
                    embed1.description = (
                        "Sorry, but no results were found... Please try again."
                    )
                    await ctx.respond(embed=embed1)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @mdSearch.command(name="author")
    async def author(self, ctx, *, author_name: Option(str, "The name of the author")):
        """Returns up to 25 authors and their info"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {"limit": 25, "name": author_name, "order[name]": "asc"}
            async with session.get(
                "https://api.mangadex.org/author", params=params
            ) as author_response:
                author_payload = await author_response.content.read()
                authorPayloadMain = jsonParser.parse(author_payload, recursive=True)
                try:
                    if len(authorPayloadMain["data"]) == 0:
                        raise NoItemsError
                    else:
                        mainPages = pages.Paginator(
                            pages=[
                                discord.Embed(
                                    title=mainItem["attributes"]["name"],
                                    description=mainItem["attributes"]["biography"],
                                )
                                .add_field(
                                    name="Created At",
                                    value=discord.utils.format_dt(
                                        ciso8601.parse_datetime(
                                            mainItem["attributes"]["createdAt"]
                                        )
                                    ),
                                    inline=True,
                                )
                                .add_field(
                                    name="Updated At",
                                    value=discord.utils.format_dt(
                                        ciso8601.parse_datetime(
                                            mainItem["attributes"]["updatedAt"]
                                        )
                                    ),
                                    inline=True,
                                )
                                .add_field(
                                    name="Twitter",
                                    value=mainItem["attributes"]["twitter"]
                                    if mainItem["attributes"]["twitter"] is not None
                                    else "None",
                                    inline=True,
                                )
                                .add_field(
                                    name="Pixiv",
                                    value=mainItem["attributes"]["pixiv"]
                                    if mainItem["attributes"]["pixiv"] is not None
                                    else "None",
                                    inline=True,
                                )
                                .add_field(
                                    name="YouTube",
                                    value=mainItem["attributes"]["youtube"]
                                    if mainItem["attributes"]["youtube"] is not None
                                    else "None",
                                    inline=True,
                                )
                                .add_field(
                                    name="Website",
                                    value=mainItem["attributes"]["website"],
                                    inline=True,
                                )
                                for mainItem in authorPayloadMain["data"]
                            ],
                            loop_pages=True,
                        )
                        await mainPages.respond(ctx.interaction, ephemeral=False)
                except NoItemsError:
                    embedValError = discord.Embed()
                    embedValError.description = (
                        "Hm, it seems like there are no results... Please try again"
                    )
                    await ctx.respond(embed=embedValError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # This will be disabled on production releases, since
    # this requires an ID input, and is not finished yet.
    # discord labs would definitely complain about this command...

    @md.command(name="read")
    async def manga_read(
        self,
        ctx: discord.ApplicationContext,
        name: Option(str, "The name of the manga"),
    ):
        """Reads a chapter out of the manga provided on MangaDex"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            params = {
                "title": name,
                "publicationDemographic[]": "none",
                "contentRating[]": "safe",
                "order[title]": "asc",
                "limit": 25,
                "includes[]": ["cover_art"],
            }
            async with session.get(
                f"https://api.mangadex.org/manga/", params=params
            ) as r:
                data = await r.content.read()
                dataMain = jsonParser.parse(data, recursive=True)
                mainPages = pages.Paginator(
                    pages=[
                        discord.Embed(
                            title=formatMangaTitles(items["attributes"]["title"])
                        )
                        for items in dataMain
                    ],
                    custom_view=SelectMangaRead(mangaData=dataMain["data"]),
                )  # the custom view will not work
                await mainPages.respond(ctx.interaction)

    #     try:
    #         async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
    #             params = {
    #                 "contentRating[]": "safe",
    #                 "includeFutureUpdates": 1,
    #                 "order[createdAt]": "asc",
    #                 "order[updatedAt]": "asc",
    #                 "order[publishAt]": "asc",
    #                 "order[readableAt]": "asc",
    #                 "order[volume]": "asc",
    #                 "order[chapter]": "asc",
    #             }
    #             async with session.get(
    #                 f"https://api.mangadex.org/manga/{manga_id}/feed", params=params
    #             ) as r:
    #                 data = await r.content.read()
    #                 dataMain = jsonParser.parse(data, recursive=True)
    #                 if "error" in dataMain["result"]:
    #                     raise NotFoundHTTPException
    #                 else:
    #                     chapterIndexID = List(dataMain["data"])[chapter_number]["id"]
    #                     chapterTitle = List(dataMain["data"])[chapter_number][
    #                         "attributes"
    #                     ]["title"]
    #                     chapterPos = List(dataMain["data"])[chapter_number][
    #                         "attributes"
    #                     ]["chapter"]
    #                     async with aiohttp.ClientSession(
    #                         json_serialize=orjson.dumps
    #                     ) as session:
    #                         async with session.get(
    #                             f"https://api.mangadex.org/at-home/server/{chapterIndexID}"
    #                         ) as r:
    #                             data2 = await r.content.read()
    #                             dataMain2 = jsonParser.parse(data2, recursive=True)
    #                             if "error" in dataMain2["result"]:
    #                                 raise NotFoundHTTPException
    #                             else:
    #                                 chapter_hash = dataMain2["chapter"]["hash"]
    #                                 paginator = pages.Paginator(
    #                                     pages=[
    #                                         discord.Embed()
    #                                         .set_footer(
    #                                             text=f"{chapterTitle} - Chapter {chapterPos}"
    #                                         )
    #                                         .set_image(
    #                                             url=f"https://uploads.mangadex.org/data/{chapter_hash}/{item}"
    #                                         )
    #                                         for item in dataMain2["chapter"]["data"]
    #                                     ],
    #                                     loop_pages=True,
    #                                 )
    #                                 await paginator.respond(
    #                                     ctx.interaction, ephemeral=False
    #                                 )
    #     except NotFoundHTTPException:
    #         embedError = discord.Embed()
    #         embedError.description = "It seems like the manga's id is invalid or cannot be found. Please try again"
    #         await ctx.respond(embed=embedError)


def setup(bot):
    bot.add_cog(MangaDex(bot))
