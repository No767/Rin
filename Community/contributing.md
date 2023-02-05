# Contributing

## Note to new contributors

When you contribute to this project, you are subject to the [Code of Conduct](./CODE_OF_CONDUCT.md). Any violations of the Code Of Conduct will be handled as stated. Read the contributing guide. **Support is not given if you didn't bother reading the documentation for setting up any of the requirements, or if you didn't bother to read the contributing guide.**

## Before Starting

Make sure to read these guides listed below:

- [Installing Requirements](./installing-requirements.md)
- [Getting Dev Discord Bot](./getting-dev-discord-bot.md)

## API Keys

Some of the API's that Rin uses requires an API key. Here's the list of all of the services that require one:

- Blue Alliance
- GitHub
- Reddit
- Tenor
- Twitter
- YouTube

## Docker Tagging Styles

Rin does have in fact a style of tagging docker images. Here it is:

- If deploying to master or production (NOTE: DO NOT DEPLOY TO PRODUCTION UNLESS IT IS FULLY TESTED AND APPROVED):
    `<image>:<github_release_tag>`
    
- If deploying to dev (GHCR):
    `<image>:edge<short_commit_sha>`

- If deployign to dev (Docker Hub):
    `<image>:edge`


## Coding Style

### Variables

Most of the code written uses `camelCasing` for variables, `PascalCasing` for classes, and `snake_casing` for ags. To sum it up:

- `camelCasing` for variables
- `PascalCasing` for classes
- `snake_casing` for args
- `ALL_CAPS` for constants
- `kebab-casing` for files

### Formatting

Rin uses pre-commit hooks to format all of the code. Make sure run `git add --all` before committing to add all of the files. More than likely you'll need to commit twice due to the formatting that pre-commit does afterwards.

### Docstrings

Just like how major programs are documented, the libraries that are custom made for Kumiko also have to be documented. The current standard for this project is to use [Google's Docstring format](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings). A handy VS Code extension that should be used is the [autoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) extension. By default it will generate the docstring in the Google format. Docstrings should be used on all coroutines and methods (excluding cogs), and on classes as well. 

For Cogs, docstrings formats are not needed. All you need to do is to add a basic docstring and Pycord will pick it up.

Example Cog:

```py 
import discord
from discord.commands import slash_command
from discord.ext import commands

class MyCog(commands.Cog):
    """An example cog for demo purposes"""
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="hello")
    async def myCommand(self, ctx: discord.ApplicationContext):
        """This is an example of a description for a slash command"""
        await ctx.respond(f"Hello {ctx.user.name}!")

def setup(bot):
    bot.add_cog(MyCog(bot))
```

## GitHub Contributing Guidelines

### Issue and Feature Requests Reports

If there is an issue or a feature you want to be added, use the built-in GitHub issue tracker. Though a system like Jira could be used, it would be more efficient to just use the issue tracker that GitHub provides. 

- If submitting a issue report, follow the template. Duplicates will not receive support
- If submitting a feature request, follow the template as well. As with issue reports, duplicate requests will not receive support

### Releasing Tags
In order to automate the release system, you have to make sure that in order to use it, the git commit message must be done correctly. Only use this if there is a new update that is ready to be released. Rin uses [SemVer](https://semver.org/) as the standard for versioning. Here's a table that should help with explaining this:

| Type of Release, Update, or Patch | Example |
|              :--:                 | :--:    | 
| Major Release (For updates that are not backwards compatible) | `Release: v2.0.0` | 
| Minor Release (For updates that are backwards compatible) | `Update: v2.5.0`|
| Patch Release (For critical security patches and bug fixes) | `Fix: v2.5.1` |


### Git Commit StyleGuides

- If updating any other files that aren't project files or not important (stuff like README.md, contributing.md, etc), add the [skip ci] label in the front
- With each new commit, the message should be more or less describing the changes. Please don't write useless commit messages...
- If releasing tags, have it in this style. `Release: [insert what changed here]`, `Update: [insert what changed here]`, and `Fix: [insert what changed here]`. Release is a major release. This means it bumps from 1.0.0 to 2.0.0. Minor means it bumps up the version from 1.4 to 1.5 for example. And fix just applies a patch, which would be 1.4.1 to 1.4.2.
