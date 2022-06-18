import asyncio
import os
import random
import datetime

import asyncpraw
import discord
import uvloop
from discord.commands import Option, slash_command
from discord.ext import commands, pages
from dotenv import load_dotenv
from rin_exceptions import NoItemsError, ThereIsaRSlashInSubreddit


load_dotenv()

Reddit_ID = os.getenv("Reddit_ID")
Reddit_Secret = os.getenv("Reddit_Secret")


class RedditV1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="reddit",
        description="Searches on reddit for content",
    )
    async def reddit(
        self,
        ctx,
        *,
        search: Option(
            str,
            "The query you want to search. Also supports searching subreddits as well",
        ),
    ):
        async with asyncpraw.Reddit(
            client_id=Reddit_ID,
            client_secret=Reddit_Secret,
            user_agent="ubuntu:rin:v2.0.0 (by /u/No767)",
        ) as api:
            original_search = search
            try:
                if "r/" in search:
                    search = search.split("/")
                    sub = search[1]
                    search = "all"
                else:
                    sub = "all"
                sub = await api.subreddit(sub)
                searcher = sub.search(query=search, limit=35)
                posts = [
                    post
                    async for post in searcher
                    if ".jpg" in post.url
                    or ".png" in post.url
                    or ".gif" in post.url
                    and not post.over_18
                ]
                try:
                    if len(posts) == 0:
                        raise NoItemsError
                    else:
                        post = random.choice(posts)
                        submission = post
                        await post.author.load()
                        reddit_embed = discord.Embed(
                            color=discord.Color.from_rgb(255, 69, 0))
                        reddit_embed.title = submission.title
                        reddit_embed.description = submission.selftext
                        # reddit_embed.description = f"{self.bot.user.name} found this post in r/{submission.subreddit.display_name} by {submission.author.name} when searching {original_search}"
                        reddit_embed.set_image(url=submission.url)
                        reddit_embed.add_field(name="Author", value=submission.author.name, inline=True)
                        reddit_embed.add_field(name="Subreddit", value=f"r/{submission.subreddit.display_name}", inline=True)
                        reddit_embed.add_field(name="URL", value=f"https://reddit.com{submission.permalink}", inline=True)
                        reddit_embed.add_field(name="Upvotes", value=submission.score, inline=True)
                        reddit_embed.add_field(name="NSFW?", value=submission.over_18, inline=True)
                        reddit_embed.add_field(name="Flair", value=submission.link_flair_text, inline=True)
                        reddit_embed.add_field(name="Number of comments", value=submission.num_comments, inline=True)
                        reddit_embed.add_field(name="Created At (UTC, 24hr)", value=datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M'), inline=True)
                        reddit_embed.add_field(name="Created At (UTC, 12hr or AM/PM)", value=datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %I:%M %p'), inline=True)
                        reddit_embed.set_thumbnail(url=post.author.icon_img)
                        await ctx.respond(embed=reddit_embed)
                except NoItemsError:
                    await ctx.respond(embed=discord.Embed(description=f"It seems like there are no posts that could be found with the query {search}. Please try again"))
            except Exception as e:
                embed = discord.Embed()
                embed.description = f"There was an error, this is likely caused by a lack of posts found in the query {original_search}. Please try again."
                embed.add_field(name="Reason", value=e, inline=True)
                await ctx.respond(embed=embed)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class RedditV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="reddit-new",
        description="Returns 25 new posts from any subreddit",
        guild_ids=[866199405090308116]
    )
    async def redditNew(
        self, ctx, *, subreddit: Option(str, "The subreddit to search")
    ):
        async with asyncpraw.Reddit(
            client_id=Reddit_ID,
            client_secret=Reddit_Secret,
            user_agent="ubuntu:rin:v2.0.0 (by /u/No767)",
        ) as redditapi:
            try:
                try:
                    if "r/" in subreddit:
                        raise ThereIsaRSlashInSubreddit
                    else:
                        mainSub = await redditapi.subreddit(subreddit)
                        mainPages = pages.Paginator(pages=[
                            discord.Embed(title=submission.title, description=submission.selftext)
                            .add_field(name="Author", value=submission.author.name, inline=True)
                            .add_field(name="Created At (UTC, 24hr)", value=datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M'), inline=True)
                            .add_field(name="Created At (UTC, 12hr or AM/PM)", value=datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %I:%M %p'), inline=True)
                            .add_field(name="ID of submission", value=submission.id, inline=True)
                            .add_field(name="Flair", value=submission.link_flair_text, inline=True)
                            .add_field(name="Number of Comments", value=submission.num_comments, inline=True)
                            .add_field(name="NSFW?", value=submission.over_18, inline=True)
                            .add_field(name="URL", value=f"https://reddit.com{submission.permalink}", inline=True)
                            .add_field(name="Upvotes", value=submission.score, inline=True)
                            .add_field(name="Spoiler?", value=submission.spoiler, inline=True)
                            .add_field(name="Upvote Ratio", value=submission.upvote_ratio, inline=True)
                            .set_image(url=submission.url)
                            async for submission in mainSub.new(limit=25)
                            ], loop_pages=True)
                        await mainPages.respond(ctx.interaction, ephemeral=False)
                except ThereIsaRSlashInSubreddit:
                    aFoolishMove = discord.Embed()
                    aFoolishMove.description = "Sorry, but you may have added the `r/` prefix of each subreddit. Please try again, but without the prefix"
                    await ctx.respond(embed=aFoolishMove)
            except Exception as e:
                embedError = discord.Embed()
                embedError.description = f"There was an error, this is likely caused by a lack of posts found in the query {subreddit}. Please try again."
                embedError.add_field(name="Reason", value=e, inline=True)
                await ctx.respond(embed=embedError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class RedditV4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="reddit-user",
        description="Provides info about the given Redditor",
    )
    async def redditor(self, ctx, *, redditor: Option(str, "The name of the Redditor")):
        async with asyncpraw.Reddit(
            client_id=Reddit_ID,
            client_secret=Reddit_Secret,
            user_agent="ubuntu:rin:v2.0.0 (by /u/No767)",
        ) as redditorApi:
            user = await redditorApi.redditor(redditor)
            await user.load()
            embedVar = discord.Embed()
            embedVar.title = user.name
            embedVar.set_thumbnail(url=user.icon_img)
            embedVar.add_field(
                name="Comment Karma", value=user.comment_karma, inline=True
            )
            embedVar.add_field(name="Created UTC",
                               value=user.created_utc, inline=True)
            embedVar.add_field(name="Link Karma",
                               value=user.link_karma, inline=True)
            await ctx.respond(embed=embedVar)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class RedditV5(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="reddit-user-comments",
        description="Returns up to 10 comments from a given Redditor",
        guild_ids=[866199405090308116]
    )
    async def redditorComments(
        self, ctx, *, redditor: Option(str, "The name of the Redditor")
    ):
        async with asyncpraw.Reddit(
            client_id=Reddit_ID,
            client_secret=Reddit_Secret,
            user_agent="ubuntu:rin:v2.0.0 (by /u/No767)",
        ) as redditorCommentsAPI:
            userComment = await redditorCommentsAPI.redditor(redditor)
            # embedVar = discord.Embed()
            # mainPages = pages.Paginator(pages=[async for comment in userComment.comments.new(limit=25)], loop_pages=True)
            async for comment in userComment.comments.new(limit=10):
                await comment.author.load()
                mainPages = pages.Paginator(pages=[discord.Embed(title=comment.author.name, description=comment.body) async for _ in userComment.comments.new(limit=10)], loop_pages=True)
                # embedVar.title = comment.author.name
                # embedVar.description = comment.body
                # embedVar.set_thumbnail(url=comment.author.icon_img)
                # await ctx.respond(embed=embedVar)
            await mainPages.respond(ctx.interaction, ephemeral=False)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class RedditV6(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="reddit-hot",
        description="Returns 25 hot posts from any subreddit",
        guild_ids=[866199405090308116]
    )
    async def redditNew(
        self, ctx, *, subreddit: Option(str, "The subreddit to search")
    ):
        async with asyncpraw.Reddit(
            client_id=Reddit_ID,
            client_secret=Reddit_Secret,
            user_agent="ubuntu:rin:v2.0.0 (by /u/No767)",
        ) as redditapi:
            try:
                try:
                    if "r/" in subreddit:
                        raise ThereIsaRSlashInSubreddit
                    else:
                        mainSub = await redditapi.subreddit(subreddit)
                        mainPages = pages.Paginator(pages=[
                            discord.Embed(title=submission.title, description=submission.selftext)
                            .add_field(name="Author", value=submission.author.name, inline=True)
                            .add_field(name="Created At (UTC, 24hr)", value=datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M'), inline=True)
                            .add_field(name="Created At (UTC, 12hr or AM/PM)", value=datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %I:%M %p'), inline=True)
                            .add_field(name="ID of submission", value=submission.id, inline=True)
                            .add_field(name="Flair", value=submission.link_flair_text, inline=True)
                            .add_field(name="Number of Comments", value=submission.num_comments, inline=True)
                            .add_field(name="NSFW?", value=submission.over_18, inline=True)
                            .add_field(name="URL", value=f"https://reddit.com{submission.permalink}", inline=True)
                            .add_field(name="Upvotes", value=submission.score, inline=True)
                            .add_field(name="Spoiler?", value=submission.spoiler, inline=True)
                            .add_field(name="Upvote Ratio", value=submission.upvote_ratio, inline=True)
                            .set_image(url=submission.url)
                            async for submission in mainSub.hot(limit=25)
                            ], loop_pages=True)
                        await mainPages.respond(ctx.interaction, ephemeral=False)
                except ThereIsaRSlashInSubreddit:
                    aFoolishMove = discord.Embed()
                    aFoolishMove.description = "Sorry, but you may have added the `r/` prefix of each subreddit. Please try again, but without the prefix"
                    await ctx.respond(embed=aFoolishMove)
            except Exception as e:
                embedError = discord.Embed()
                embedError.description = f"There was an error, this is likely caused by a lack of posts found in the query {subreddit}. Please try again."
                embedError.add_field(name="Reason", value=e, inline=True)
                await ctx.respond(embed=embedError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class RedditV7(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="reddit-top",
        description="Returns 25 top posts from any subreddit",
        guild_ids=[866199405090308116]
    )
    async def redditNew(
        self, ctx, *, subreddit: Option(str, "The subreddit to search")
    ):
        async with asyncpraw.Reddit(
            client_id=Reddit_ID,
            client_secret=Reddit_Secret,
            user_agent="ubuntu:rin:v2.0.0 (by /u/No767)",
        ) as redditapi:
            try:
                try:
                    if "r/" in subreddit:
                        raise ThereIsaRSlashInSubreddit
                    else:
                        mainSub = await redditapi.subreddit(subreddit)
                        mainPages = pages.Paginator(pages=[
                            discord.Embed(title=submission.title, description=submission.selftext)
                            .add_field(name="Author", value=submission.author.name, inline=True)
                            .add_field(name="Created At (UTC, 24hr)", value=datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M'), inline=True)
                            .add_field(name="Created At (UTC, 12hr or AM/PM)", value=datetime.datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %I:%M %p'), inline=True)
                            .add_field(name="ID of submission", value=submission.id, inline=True)
                            .add_field(name="Flair", value=submission.link_flair_text, inline=True)
                            .add_field(name="Number of Comments", value=submission.num_comments, inline=True)
                            .add_field(name="NSFW?", value=submission.over_18, inline=True)
                            .add_field(name="URL", value=f"https://reddit.com{submission.permalink}", inline=True)
                            .add_field(name="Upvotes", value=submission.score, inline=True)
                            .add_field(name="Spoiler?", value=submission.spoiler, inline=True)
                            .add_field(name="Upvote Ratio", value=submission.upvote_ratio, inline=True)
                            .set_image(url=submission.url)
                            async for submission in mainSub.top("all", limit=25)
                            ], loop_pages=True)
                        await mainPages.respond(ctx.interaction, ephemeral=False)
                except ThereIsaRSlashInSubreddit:
                    aFoolishMove = discord.Embed()
                    aFoolishMove.description = "Sorry, but you may have added the `r/` prefix of each subreddit. Please try again, but without the prefix"
                    await ctx.respond(embed=aFoolishMove)
            except Exception as e:
                embedError = discord.Embed()
                embedError.description = f"There was an error, this is likely caused by a lack of posts found in the query {subreddit}. Please try again."
                embedError.add_field(name="Reason", value=e, inline=True)
                await ctx.respond(embed=embedError)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def setup(bot):
    bot.add_cog(RedditV1(bot))
    # bot.add_cog(RedditV2(bot))
    # bot.add_cog(RedditV3(bot))
    # bot.add_cog(RedditV4(bot))
    # bot.add_cog(RedditV5(bot))
    # bot.add_cog(RedditV6(bot))
    # bot.add_cog(RedditV7(bot))
