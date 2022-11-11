"""
RilowBot
-----------------------------
File: checks.py
Date: 2022-11-10
Updated: 2022-11-10

Contains various checks to be used for commands.
"""
import discord
from discord.ext import commands

# My id is hardcoded just in-case.
RILOW_ID = 254077906152718340

class Checks:
    bot: commands.Bot = None

    @classmethod
    async def global_check(cls, ctx: commands.Context) -> bool:
        """
        A check that runs on every command. Used for indev checking.
        """
        indev = cls.bot.config.indev
        return (indev and await cls.is_bot_admin(ctx)) or not indev

    @classmethod
    async def is_bot_admin(cls, ctx: commands.Context) -> bool:
        """
        A check that returns True if the author is a bot admin.
        """
        return ctx.author.id == RILOW_ID\
            or ctx.author.id in cls.bot.config.get("admin_ids", [])


def setup(bot: commands.Bot) -> None:
    Checks.bot = bot
    bot.check(Checks.global_check)