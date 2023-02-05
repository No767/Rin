import asyncio
import os

import aiohttp
import ciso8601
import discord
import orjson
import simdjson
import uvloop
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands, pages
from discord.utils import format_dt
from dotenv import load_dotenv
from rin_exceptions import HTTPException, NoItemsError

jsonParser = simdjson.Parser()

load_dotenv()

GITHUB_API_KEY = os.getenv("GitHub_API_Access_Token")


class GitHub(commands.Cog):
    """Commands for getting data from GitHub"""

    def __init__(self, bot):
        self.bot = bot

    github = SlashCommandGroup("github", "GitHub commands")
    githubUser = github.create_subgroup("user", "GitHub user commands")
    githubSearch = github.create_subgroup("search", "Search for repositories on GitHub")
    githubIssuesGroup = github.create_subgroup("issues", "Search for issues on GitHub")
    githubReleases = github.create_subgroup("releases", "Search for releases on GitHub")

    @githubSearch.command(name="repos")
    async def githubRepos(self, ctx, *, repo: Option(str, "The name of the repo")):
        """Searches for repositories on GitHub"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {
                "Authorization": f"token {GITHUB_API_KEY}",
                "accept": "application/vnd.github.v3+json",
            }
            params = {"q": repo, "sort": "stars", "order": "desc", "per_page": 25}
            async with session.get(
                "https://api.github.com/search/repositories",
                headers=headers,
                params=params,
            ) as r:
                try:
                    data = await r.content.read()
                    dataMain = jsonParser.parse(data, recursive=True)
                    try:
                        if len(dataMain["items"]) == 0:
                            raise NoItemsError
                        else:
                            mainPages = pages.Paginator(
                                pages=[
                                    discord.Embed(
                                        title=mainItem["name"],
                                        description=mainItem["description"],
                                    )
                                    .add_field(
                                        name="URL",
                                        value=mainItem["html_url"],
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Private",
                                        value=mainItem["private"],
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Fork", value=mainItem["fork"], inline=True
                                    )
                                    .add_field(
                                        name="Creation Date",
                                        value=format_dt(
                                            ciso8601.parse_datetime(
                                                mainItem["created_at"]
                                            )
                                        ),
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Homepage",
                                        value=f"[{mainItem['homepage']}]",
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Stars",
                                        value=mainItem["stargazers_count"],
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Language",
                                        value=mainItem["language"],
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Forks Count",
                                        value=mainItem["forks_count"],
                                        inline=True,
                                    )
                                    .set_thumbnail(url=mainItem["owner"]["avatar_url"])
                                    for mainItem in dataMain["items"]
                                ]
                            )
                            await mainPages.respond(ctx.interaction, ephemeral=False)
                    except NoItemsError:
                        embedNoItemsError = discord.Embed()
                        embedNoItemsError.description = f"Sorry, there seems to be no repos named {repo}. Please try again"
                        await ctx.respond(embed=embedNoItemsError)

                except Exception:
                    embedError = discord.Embed()
                    embedError.description = (
                        "Sorry, but something went wrong. Please try again"
                    )
                    await ctx.respond(embed=embedError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @githubSearch.command(name="users")
    async def githubSearchUsers(
        self, ctx, *, user: Option(str, "The user on GitHub to search")
    ):
        """Searches for users on GitHub"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {
                "Authorization": f"token {GITHUB_API_KEY}",
                "accept": "application/vnd.github.v3+json",
            }
            params = {"q": user, "sort": "stars", "order": "desc", "per_page": 25}
            async with session.get(
                "https://api.github.com/search/users", headers=headers, params=params
            ) as response:
                try:
                    try:
                        data = await response.content.read()
                        dataMain = jsonParser.parse(data, recursive=True)
                        if len(dataMain["items"]) == 0:
                            raise NoItemsError
                        else:
                            mainPages = pages.Paginator(
                                pages=[
                                    discord.Embed(title=dictItem["login"])
                                    .add_field(
                                        name="Type", value=dictItem["type"], inline=True
                                    )
                                    .add_field(
                                        name="URL",
                                        value=dictItem["html_url"],
                                        inline=True,
                                    )
                                    .set_thumbnail(url=dictItem["avatar_url"])
                                    for dictItem in dataMain["items"]
                                ],
                                loop_pages=True,
                            )
                            await mainPages.respond(ctx.interaction, ephemeral=False)
                    except NoItemsError:
                        embedNoItemsError = discord.Embed()
                        embedNoItemsError.description = f"Sorry, there seems to be no users named {user}. Please try again"
                        await ctx.respond(embed=embedNoItemsError)
                except Exception:
                    embedError = discord.Embed()
                    embedError.description = (
                        "Sorry, but something went wrong. Please try again"
                    )
                    embedError.set_footer(
                        text="Sometimes this may be the description of the repo being too big."
                    )
                    await ctx.respond(embed=embedError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @githubIssuesGroup.command(name="all")
    async def githubIssuesRepo(
        self,
        ctx,
        *,
        owner: Option(str, "The owner of the repo"),
        repo: Option(str, "The name of the repo"),
        state: Option(
            str,
            "Whether an issue has been open or closed (or all)",
            choices=["Open", "Closed", "All"],
        ),
    ):
        """Gets all issues from a repo"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {
                "Authorization": f"token {GITHUB_API_KEY}",
                "accept": "application/vnd.github.v3+json",
            }
            params = {
                "state": str(state).lower(),
                "sort": "created",
                "per_page": 25,
                "direction": "desc",
            }
            async with session.get(
                f"https://api.github.com/repos/{owner}/{repo}/issues",
                headers=headers,
                params=params,
            ) as r:
                try:
                    data = await r.content.read()
                    dataMain = jsonParser.parse(data, recursive=True)
                    try:
                        try:
                            if len(dataMain) == 0:
                                raise NoItemsError
                            elif r.status == 404:
                                raise HTTPException
                            else:

                                mainPages = pages.Paginator(
                                    pages=[
                                        discord.Embed(
                                            title=mainItem3["title"],
                                            description=mainItem3["body"],
                                        )
                                        .add_field(
                                            name="URL",
                                            value=mainItem3["html_url"],
                                            inline=True,
                                        )
                                        .add_field(
                                            name="Issue State",
                                            value=mainItem3["state"],
                                            inline=True,
                                        )
                                        .add_field(
                                            name="Issue Number",
                                            value=mainItem3["number"],
                                            inline=True,
                                        )
                                        .add_field(
                                            name="Issue Created",
                                            value=format_dt(
                                                ciso8601.parse_datetime(
                                                    mainItem3["created_at"]
                                                )
                                            ),
                                            inline=True,
                                        )
                                        .add_field(
                                            name="Issue Updated",
                                            value=format_dt(
                                                ciso8601.parse_datetime(
                                                    mainItem3["updated_at"]
                                                )
                                            ),
                                            inline=True,
                                        )
                                        .add_field(
                                            name="Label",
                                            value=[
                                                labelItemMain["name"]
                                                for labelItemMain in mainItem3["labels"]
                                            ],
                                            inline=True,
                                        )
                                        .add_field(
                                            name="Comments", value=mainItem3["comments"]
                                        )
                                        .add_field(
                                            name="Assigness",
                                            value=[
                                                item4["login"]
                                                for item4 in mainItem3["assignees"]
                                            ],
                                            inline=True,
                                        )
                                        .add_field(
                                            name="Reporter",
                                            value=mainItem3["user"]["login"],
                                            inline=True,
                                        )
                                        .set_thumbnail(
                                            url=mainItem3["user"]["avatar_url"]
                                        )
                                        for mainItem3 in dataMain
                                    ],
                                    loop_pages=True,
                                )
                                await mainPages.respond(
                                    ctx.interaction, ephemeral=False
                                )
                        except HTTPException:
                            await ctx.respond(
                                embed=discord.Embed(
                                    description="It seems like that there isn't a repo with that name. Please try again"
                                )
                            )
                    except NoItemsError:
                        embedNoItemsError = discord.Embed()
                        embedNoItemsError.description = f"Sorry, there seems to be no issues in that repo. Please try again"
                        await ctx.respond(embed=embedNoItemsError)
                except Exception:
                    embedError = discord.Embed()
                    embedError.description = (
                        "It seems like there was a error. Please try again"
                    )
                    await ctx.respond(embed=embedError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @githubIssuesGroup.command(name="one")
    async def githhubIssuesRepoOne(
        self,
        ctx,
        owner: Option(str, "The owner of the repo"),
        repo: Option(str, "The name of the repo"),
        issue_number: Option(str, "The number for the issue on GitHub"),
    ):
        """Gets info about one issue on any repo on GitHub"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {
                "Authorization": f"token {GITHUB_API_KEY}",
                "accept": "application/vnd.github.v3+json",
            }
            async with session.get(
                f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}",
                headers=headers,
            ) as r:
                try:
                    if r.status == 404:
                        raise HTTPException
                    else:
                        data = await r.content.read()
                        dataMain = jsonParser.parse(data, recursive=True)
                        embed = discord.Embed()
                        embed.title = dataMain["title"]
                        embed.description = dataMain["body"]
                        embed.add_field(
                            name="User Profile", value=dataMain["user"]["html_url"]
                        )
                        embed.add_field(name="State", value=dataMain["state"])
                        embed.add_field(
                            name="Labels",
                            value=str(dataMain["labels"]).replace("'", ""),
                        )
                        embed.add_field(
                            name="Assignees",
                            value=str(dataMain["assignees"]).replace("'", ""),
                        )
                        embed.add_field(
                            name="Created At",
                            value=format_dt(
                                ciso8601.parse_datetime(dataMain["created_at"])
                            ),
                        )
                        embed.add_field(
                            name="Updated At",
                            value=format_dt(
                                ciso8601.parse_datetime(dataMain["updated_at"])
                            ),
                        )
                        embed.set_thumbnail(url=dataMain["user"]["avatar_url"])
                        await ctx.respond(embed=embed)
                except HTTPException:
                    embedHTTPExceptionError = discord.Embed()
                    embedHTTPExceptionError.description = "It seems like that there isn't an issue with that number. Please try again"
                    await ctx.respond(embed=embedHTTPExceptionError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @githubReleases.command(name="list")
    async def githubReleasesList(
        self,
        ctx,
        *,
        owner: Option(str, "The owner of the repo"),
        repo: Option(str, "The name of the repo"),
    ):
        """Lists out up to 25 releases of any repo"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {
                "Authorization": f"token {GITHUB_API_KEY}",
                "accept": "application/vnd.github.v3+json",
            }
            params = {"per_page": 25}
            async with session.get(
                f"https://api.github.com/repos/{owner}/{repo}/releases",
                headers=headers,
                params=params,
            ) as r:
                try:

                    data = await r.content.read()
                    dataMain = jsonParser.parse(data, recursive=True)
                    try:
                        if r.status == 404:
                            raise HTTPException
                        elif len(dataMain) == 0:
                            raise NoItemsError
                        else:
                            mainPages = pages.Paginator(
                                pages=[
                                    discord.Embed(
                                        title=dictItem5["name"],
                                        description=dictItem5["body"],
                                    )
                                    .add_field(
                                        name="URL",
                                        value=dictItem5["html_url"],
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Created At",
                                        value=ciso8601.parse_datetime(
                                            dictItem5["created_at"]
                                        ),
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Published At",
                                        value=format_dt(
                                            ciso8601.parse_datetime(
                                                dictItem5["published_at"]
                                            )
                                        ),
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Tarball URL",
                                        value=dictItem5["tarball_url"],
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Zipball URL",
                                        value=dictItem5["zipball_url"],
                                    )
                                    .add_field(
                                        name="Author",
                                        value=dictItem5["author"]["login"],
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Download URL",
                                        value=str(
                                            [
                                                items5["browser_download_url"]
                                                for items5 in dictItem5["assets"]
                                            ]
                                        ).replace("'", ""),
                                        inline=True,
                                    )
                                    .add_field(
                                        name="Download Count",
                                        value=str(
                                            [
                                                items6["download_count"]
                                                for items6 in dictItem5["assets"]
                                            ]
                                        ).replace("'", ""),
                                        inline=True,
                                    )
                                    .set_thumbnail(
                                        url=dictItem5["author"]["avatar_url"]
                                    )
                                    for dictItem5 in dataMain
                                ],
                                loop_pages=True,
                            )
                            await mainPages.respond(ctx.interaction, ephemeral=False)
                    except NoItemsError:
                        await ctx.respond(
                            embed=discord.Embed(
                                description="It seems like that there isn't a release for that repo. Please try again"
                            )
                        )
                except HTTPException:
                    embedHTTPExceptionError = discord.Embed()
                    embedHTTPExceptionError.description = "Sorry, there seems to be no releases in that repo. Please try again"
                    await ctx.respond(embed=embedHTTPExceptionError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @githubReleases.command(name="latest")
    async def githubLatestRelease(
        self,
        ctx,
        *,
        owner: Option(str, "The owner of the repo"),
        repo: Option(str, "The repo's name"),
    ):
        """Gets the latest published full release for any repo"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {
                "Authorization": f"token {GITHUB_API_KEY}",
                "accept": "application/vnd.github.v3+json",
            }
            async with session.get(
                f"https://api.github.com/repos/{owner}/{repo}/releases/latest",
                headers=headers,
            ) as r:
                data = await r.content.read()
                dataMain = jsonParser.parse(data, recursive=True)
                try:
                    if r.status == 404:
                        raise HTTPException
                    else:
                        pageGroupsList = [
                            pages.PageGroup(
                                pages=[
                                    discord.Embed(
                                        title=dataMain["name"],
                                        description=dataMain["body"],
                                    )
                                    .add_field(name="URL", value=dataMain["html_url"])
                                    .add_field(
                                        name="Pre-release?",
                                        value=dataMain["prerelease"],
                                    )
                                    .add_field(name="Tag", value=dataMain["tag_name"])
                                    .add_field(
                                        name="Author", value=dataMain["author"]["login"]
                                    )
                                    .add_field(
                                        name="Created At",
                                        value=format_dt(
                                            ciso8601.parse_datetime(
                                                dataMain["created_at"]
                                            )
                                        ),
                                    )
                                    .add_field(
                                        name="Updated At",
                                        value=format_dt(
                                            ciso8601.parse_datetime(
                                                dataMain["published_at"]
                                            )
                                        )
                                        if dataMain["published_at"] is not None
                                        else "None",
                                    )
                                ],
                                label="Release Information",
                                description="Page for release information",
                            ),
                            pages.PageGroup(
                                pages=[
                                    discord.Embed(
                                        title=item["name"], description=item["label"]
                                    )
                                    .add_field(
                                        name="URL", value=item["browser_download_url"]
                                    )
                                    .add_field(
                                        name="Uploader", value=item["uploader"]["login"]
                                    )
                                    .add_field(name="Size", value=item["size"])
                                    .add_field(
                                        name="Content Type", value=item["content_type"]
                                    )
                                    .add_field(
                                        name="Download Count",
                                        value=item["download_count"],
                                    )
                                    .add_field(
                                        name="Created At",
                                        value=format_dt(
                                            ciso8601.parse_datetime(item["created_at"])
                                        ),
                                    )
                                    for item in dataMain["assets"]
                                ],
                                label="Assets",
                                description="Page for downloadable assets and information",
                            ),
                        ]
                        mainPages = pages.Paginator(
                            pages=pageGroupsList, show_menu=True, loop_pages=True
                        )
                        await mainPages.respond(ctx.interaction)
                except HTTPException:
                    embedHTTPExceptionError = discord.Embed()
                    embedHTTPExceptionError.description = "Sorry, but it seems like either there was no release or the repo doesn't exist. Please try again"
                    await ctx.respond(embed=embedHTTPExceptionError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @github.command(name="repo")
    async def githubReposInfo(
        self,
        ctx,
        *,
        owner: Option(str, "The owner of the repo"),
        repo: Option(str, "The name of the repo"),
    ):
        """Returns info about any repo"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {
                "Authorization": f"token {GITHUB_API_KEY}",
                "accept": "application/vnd.github.v3+json",
            }
            async with session.get(
                f"https://api.github.com/repos/{owner}/{repo}", headers=headers
            ) as r:
                data = await r.content.read()
                dataMain = jsonParser.parse(data, recursive=True)
                embedMain = discord.Embed()
                embedFilter = [
                    "permissions",
                    "owner",
                    "template_repository",
                    "organization",
                    "source",
                    "parent",
                    "license",
                    "url",
                    "archive_url",
                    "assignees_url",
                    "blobs_url",
                    "branches_url",
                    "collaborators_url",
                    "commits_url",
                    "comments_url",
                    "compare_url",
                    "contributors_url",
                    "deployments_url",
                    "downloads_url",
                    "events_url",
                    "forks_url",
                    "git_commits_url",
                    "git_refs_url",
                    "git_tags_url",
                    "git_url",
                    "issue_comment_url",
                    "issue_events_url",
                    "issues_url",
                    "keys_url",
                    "labels_url",
                    "languages_url",
                    "merges_url",
                    "milestones_url",
                    "notifications_url",
                    "pulls_url",
                    "releases_url",
                    "stargazers_urls",
                    "statuses_url",
                    "subscribers_url",
                    "subscription_url",
                    "tags_url",
                    "teams_url",
                    "trees_url",
                    "clone_url",
                    "mirror_url",
                    "hooks_url",
                    "svn_url",
                    "contents_url",
                    "description",
                    "id",
                    "node_id",
                    "name",
                    "created_at",
                    "updated_at",
                    "pushed_at",
                    "stargazers_url",
                    "has_issues",
                    "has_projects",
                    "has_downloads",
                    "has_wiki",
                    "has_pages",
                    "temp_clone_token",
                    "allow_squash_merge",
                    "is_template",
                    "web_commit_signoff_required",
                    "size",
                    "archived",
                    "disabled",
                    "allow_forking",
                    "allow_merge_commit",
                    "allow_rebase_merge",
                    "allow_auto_merge",
                    "delete_branch_on_merge",
                    "allow_update_branch",
                    "default_branch",
                    "visibility",
                    "ssh_url",
                    "fork",
                    "private",
                    "use_squash_pr_title_as_default",
                ]
                licenseFilter = ["key", "url", "spdx_id", "node_id", "html_url"]
                try:
                    if r.status == 404:
                        raise HTTPException
                    else:
                        for keys, value in dataMain.items():
                            if keys not in embedFilter:
                                embedMain.add_field(
                                    name=keys, value=f"[{value}]", inline=True
                                )
                        for k, v in dataMain["license"].items():
                            if k not in licenseFilter:
                                embedMain.add_field(
                                    name=f"License {k}", value=f"[{v}]", inline=True
                                )
                        embedMain.add_field(
                            name="created_at",
                            value=format_dt(
                                ciso8601.parse_datetime(dataMain["created_at"])
                            ),
                            inline=True,
                        )
                        embedMain.add_field(
                            name="updated_at",
                            value=format_dt(
                                ciso8601.parse_datetime(dataMain["updated_at"])
                            ),
                            inline=True,
                        )
                        embedMain.add_field(
                            name="pushed_at",
                            value=format_dt(
                                ciso8601.parse_datetime(dataMain["pushed_at"])
                            ),
                            inline=True,
                        )
                        embedMain.title = dataMain["name"]
                        embedMain.description = dataMain["description"]
                        embedMain.set_thumbnail(url=dataMain["owner"]["avatar_url"])
                        await ctx.respond(embed=embedMain)
                except HTTPException:
                    embedHTTPExceptionError = discord.Embed()
                    embedHTTPExceptionError.description = "Sorry, it seems like there is no repo named like that. Please try again"
                    await ctx.respond(embed=embedHTTPExceptionError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    @githubUser.command(name="one")
    async def githubUserSearch(
        self, ctx, *, username: Option(str, "The username to search")
    ):
        """Returns info on a user in GitHub"""
        async with aiohttp.ClientSession(json_serialize=orjson.dumps) as session:
            headers = {
                "Authorization": f"token {GITHUB_API_KEY}",
                "accept": "application/vnd.github.v3+json",
            }
            async with session.get(
                f"https://api.github.com/users/{username}", headers=headers
            ) as r:
                data = await r.content.read()
                dataMain = jsonParser.parse(data, recursive=True)
                embedMain = discord.Embed()
                mainFilterEmbed = [
                    "url",
                    "followers_url",
                    "following_url",
                    "gists_url",
                    "starred_url",
                    "subscriptions_url",
                    "organizations_url",
                    "repos_url",
                    "events_url",
                    "received_events_url",
                    "name",
                    "bio",
                    "login",
                    "gravatar_id",
                    "avatar_url",
                    "plan",
                ]
                try:
                    if r.status == 404:
                        raise HTTPException
                    else:
                        for keys, value in dataMain.items():
                            if keys not in mainFilterEmbed:
                                embedMain.add_field(
                                    name=keys, value=f"[{value}]", inline=True
                                )
                        embedMain.title = f"{dataMain['login']} - {dataMain['name']}"
                        embedMain.description = dataMain["bio"]
                        embedMain.set_thumbnail(url=dataMain["avatar_url"])
                        await ctx.respond(embed=embedMain)
                except HTTPException:
                    embedHTTPExceptionError = discord.Embed()
                    embedHTTPExceptionError.description = "Sorry, it seems like there is no org named like that. Please try again"
                    await ctx.respond(embed=embedHTTPExceptionError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def setup(bot):
    bot.add_cog(GitHub(bot))
