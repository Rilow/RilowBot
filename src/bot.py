"""
RilowBot
-----------------------------
File: bot.py
Date: 2022-11-10
Updated: 2022-11-10

The core bot.
"""
import logging
import discord
from discord.ext import commands
import sys

from util import rlog
from util.lang import Lang
from util.config import Config
from secrets import TOKEN

# The default prefix to use.
DEFAULT_PREFIX = "."

# The extensions to load right when the bot starts.
INITIAL_EXTENSIONS = [
    # NOTE: THIS MUST ALWAYS BE LOADED.
    "util.checks",

    "system"
]

class RilowBot(commands.Bot):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

        self.config = Config("config.json")
        self.data = Config("data.json")
        self.lang = Lang()

        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=self._get_prefix, 
            intents=intents
        )
    
    def _get_prefix(self, bot: commands.Bot, message: discord.Message) -> str:
        return self.data.get(message.guild.id, {})\
                            .get("prefix", DEFAULT_PREFIX)
    

    async def on_ready(self) -> None:
        """
        Called when the bot is fully ready and running.
        """
        self._logger.info("Bot ready!")

    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        Called when a command raises an unhandled exception.
        """
        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.send(f"`{error.args[0]}`")
        else:
            ## Unhandled / Unknown exceptions.
            fmt = rlog.format_exception(error)
            logging.fatal(f"Unhandled exception: \n{fmt}")
            await ctx.send(f"An unknown exception ocurred.")

if __name__ == "__main__":
    rlog.init_logging()

    bot = RilowBot()

    bot.load_extensions(*INITIAL_EXTENSIONS)
    bot.run(TOKEN)
        