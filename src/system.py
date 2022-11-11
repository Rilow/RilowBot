"""
RilowBot
-----------------------------
File: system.py
Date: 2022-11-10
Updated: 2022-11-10

The System module contains commands useful for development/bot admin
purposes. These are NOT used by server admins and instead are used by
the BOT admins.
"""
import io
import json
import logging
import sys
from typing import Callable, Optional
import discord
from discord.ext import commands

from util.checks import Checks
from util.rlog import format_exception

class SystemCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._logger = logging.getLogger(__name__)
        
        self.bot = bot
    
    async def _send(self, ctx: commands.Context, msg: str, *, func: Optional[Callable]=print) -> None:
        """
        Internal method to send text.
        Will send in discord if indev mode is enabled.

        `func` indicates the function to be used when
        indev mode is false. Defaults to `print`.
        """
        if self.bot.config.indev:
            await ctx.send(f"```{msg}```")
        else:
            func(msg)

    @commands.command(hidden=True)
    async def ping(self, ctx: commands.Context) -> None:
        """Check if the bot is alive.
        
        Usage: .ping
        """
        await ctx.send("Pong!")
    
    @commands.command(hidden=True)
    @commands.check(Checks.is_bot_admin)
    async def exit(self, ctx: commands.Context) -> None:
        """Exits the bot.
        
        Usage: .exit
        """
        await ctx.message.delete()

        self._logger.info("Starting shutdown...")

        await self.bot.close()

        self._logger.info("Done shutdown.")
        sys.exit(0)

    @commands.command(hidden=True)
    @commands.check(Checks.is_bot_admin)
    async def indev(self, ctx: commands.Context) -> None:
        """Toggles the indev flag.
        
        Usage: .indev
        """
        await ctx.message.delete()

        try:
            self.bot.config.indev = not self.bot.config.indev
        except KeyError:
            self.bot.config.indev = True
            self.bot.config._save()

        self._logger.info(f"{ctx.author.name} toggled indev to {self.bot.config.indev}")

    @commands.command(hidden=True)
    @commands.check(Checks.is_bot_admin)
    async def config(self, ctx: commands.Context, *, key=None) -> None:
        """Config lookup.
        
        Usage: .config [key]
        """
        await ctx.message.delete()

        # Specifing `reload` as the key actually
        # invokes a subcommand which reloads the config.
        if key == "reload":
            self.bot.config._load()
            return await self._send(ctx, "Config reloaded.", func=self._logger.info)

        # Otherwise just display the data.
        if key is None:
            data = "json\n" + json.dumps(self.bot.config._data, sort_keys=True, indent=4)\
                    .replace(",\n", ",\n\n")
        else:
            data = str(self.bot.config[data])
        
        await self._send(ctx, data)
        
    @commands.command(hidden=True)
    @commands.check(Checks.is_bot_admin)
    async def code(self, ctx: commands.Context, *, code=None) -> None:
        """Runs code on the host machine.
        
        Usage: .code <code>
        """
        await ctx.message.delete()

        if code is None: return

        globals_ = {
            "bot": self.bot,
            "config": self.bot.config,
            "data": self.bot.data,
            "lang": self.bot.lang,
        }
        
        s = io.StringIO()
        sys.stdout = s

        try:
            res = eval(code, globals_)
        except Exception as exc:
            f = format_exception(exc)

            sys.stdout = sys.__stdout__
            logging.error(f"Exception in code: \n{f}")
        
        else:
            result = res or s.getvalue()

            sys.stdout = sys.__stdout__

            await self._send(ctx, result)

    @commands.command(hidden=True)
    @commands.check(Checks.is_bot_admin)
    async def load(self, ctx: commands.Context, ext: str) -> None:
        """Load an extension.
        
        Usage: .load <extension>
        """
        await ctx.message.delete()

        try:
            self.bot.load_extension(ext)
        except discord.errors.ExtensionAlreadyLoaded:
            await self._send(ctx, f"Extension {ext} already loaded.", func=self._logger.warn)
        else:
            await self._send(ctx, f"Extension {ext} loaded.", func=self._logger.info)
    
    @commands.command(hidden=True)
    @commands.check(Checks.is_bot_admin)
    async def unload(self, ctx: commands.Context, ext: str) -> None:
        """Unload an extension.
        
        Usage: .unload <extension>
        """
        await ctx.message.delete()

        try:
            self.bot.unload_extension(ext)
        except discord.errors.ExtensionNotLoaded:
            await self._send(ctx, f"Extension {ext} is not loaded.", func=self._logger.warn)
        else:
            await self._send(ctx, f"Extension {ext} unloaded.", func=self._logger.info)
    
    @commands.command(hidden=True)
    @commands.check(Checks.is_bot_admin)
    async def reload(self, ctx: commands.Context, ext: str) -> None:
        """Reload an extension.
        
        Usage: .reload <extension>
        """
        await ctx.message.delete()

        try:
            self.bot.reload_extension(ext)
        except discord.errors.ExtensionNotLoaded:
            await self._send(ctx, f"Extension {ext} is not laoded.", func=self._logger.warn)
        else:
            await self._send(ctx, f"Extension {ext} reloaded.", func=self._logger.info)

def setup(bot: commands.Bot) -> None:
    """
    Setup the system cog.
    """
    bot.add_cog(SystemCog(bot))