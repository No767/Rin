# 🛠️ Rin V2.2.8 (LTS) 🛠️

This update removes some of the stuff that was causing issues in v2.2.7. And also adds some new improvements to the features.
## 🛠️ Changes

- Bump version to `v2.2.8`
- Completely rewrite the `help` command
- Merged ungrouped commands into the `rin` cog (except for `help`)
- Fixed TBA Matches Team command being broken with future events (#265)
- Move Dockerfiles into a separate Docker folder for cleanup
- Rename all of the Cogs + Add Cog docstrings

## ✨ Additions

- New `help` command system

## ➖ Removals

- Removed `bot-info.py` cog (Merged into `rin` cog)
- Removed `rinhelp.py` cog (Merged into `rin` cog)
- Removed `rininfo.py` cog (Merged into `rin` cog)
- Removed `rininvite.py` cog (Merged into `rin` cog)
- Removed `rinping.py` cog (Merged into `rin` cog)
- Removed `uptime.py` cog (Merged into `rin` cog)
- Removed `version.py` cog (Merged into `rin` cog)

## ⬆️ Dependency Updates

- \[pip](deps)\: Bump aiohttp from 3.8.1 to 3.8.3 (@dependabot)
- \[Actions](deps)\: Bump actions/setup-node from 3.4.1 to 3.5.0 (@dependabot)
- \[pip](deps)\: Bump py-cord from 2.1.3 to 2.2.0 (@dependabot)
- \[pip](deps)\: Bump py-cord from 2.2.0 to 2.2.2 (@dependabot)