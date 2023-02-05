# ✨ Rin V2.3.0 ✨

This update removes a ton of old unused cogs, and is a general improvement update.

## :boom: Breaking Changes :boom:

- **Dropped Support for Alpine-based images and `-alpine` tags**. This means v2.2.x will be the last supported version to have Alpine Linux as a base. Debian 11 will now be the new base. See [this gist](https://gist.github.com/No767/76d87bce5e6fcb1e682d2ff932c2a6b7) for more info. (The gist is originally meant for Kumiko and Akari, but contains the same reason why for Rin as well).
- **Migrated from Pipenv to Poetry**. This was done because of pipenv's slow lock times. 

## ✨ TD;LR

- Major code cleanup
- Dropped Alpine Linux builds

## 🛠️ Changes

- Upgrade Rin to Python 3.11
- Revamped MangaDex and Blue Alliance commands
- Use PageGroups for Blue Alliance, MangaDex, and GitHub cogs
- Subclass Rin
- Use recursive globs for cog loading
- Swap from Python Dateutil to CISO8601
- Fix Dockerfile issues

## ✨ Additions

- Added an interaction failure handler (to handle errors, ported from Kumiko)
- Improved and new MD Search command
- MD Read command (not enabled, but in the works)

## ➖ Removals

- Hypixel, Twitch, Discord Bots, First FRC, and Top.gg cogs
- Snyk workflow
- Alpine Dockerfiles and workflows
- Env variables (`DISCORD_BOTS_API_KEY`, `FIRST_EVENTS_FINAL_KEY`, `HYPIXEL_API_KEY`, `TOP_GG_API_KEY`, `TWITCH_API_ACCESS_TOKEN`, and `TWITCH_API_CLIENT_ID`)

## ⬆️ Dependency Updates

- \[pip](deps)\: Bump numpy from 1.23.3 to 1.23.4 (@dependabot)
- \[Actions](deps)\: Bump actions/setup-node from 3.5.0 to 3.5.1 (@dependabot)
- \[pip](deps)\: Bump asyncpraw from 7.5.0 to 7.6.0 (@dependabot)
- \[pip](deps)\: Bump orjson from 3.8.0 to 3.8.1 (@dependabot)
- \[Actions](deps)\: Bump mathieudutour/github-tag-action from 6.0 to 6.1 (@dependabot)
- \[pip](deps)\: Bump orjson from 3.8.1 to 3.8.2 (@dependabot)
- \[pip](deps)\: Bump py-cord from 2.2.2 to 2.3.0 (@dependabot)
- \[pip](deps)\: Bump py-cord from 2.3.0 to 2.3.1 (@dependabot)
- \[pip](deps)\: Bump asyncpraw from 7.6.0 to 7.6.1 (@dependabot)
- \[pip](deps)\: Bump orjson from 3.8.2 to 3.8.3 (@dependabot)
- \[pip](deps)\: Bump numpy from 1.23.5 to 1.24.0 (@dependabot)
- \[pip](deps)\: Bump numpy from 1.24.0 to 1.24.1 (@dependabot)
- \[pip](deps)\: Bump orjson from 3.8.3 to 3.8.4 (@dependabot)
- \[Actions](deps)\: Bump actions/cache from 3.2.2 to 3.2.3 (@dependabot)
- \[pip](deps)\: Bump orjson from 3.8.4 to 3.8.5 (@dependabot)
- \[Actions](deps)\: Bump actions/setup-python from 4.4.0 to 4.5.0 (@dependabot)
- \[pip](deps)\: Bump python-dotenv from 0.21.0 to 0.21.1 (@dependabot)
- \[Actions](deps)\: Bump actions/cache from 3.2.3 to 3.2.4 (@dependabot)
- \[Actions](deps)\: Bump docker/build-push-action from 3 to 4 (@dependabot)
- \[pip](deps)\: Bump tortoise-orm from 0.19.2 to 0.19.3 (@dependabot)