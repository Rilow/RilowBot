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

from util import rlog
from util.lang import Lang
from util.config import Config
from secrets import TOKEN

# The default prefix to use.
DEFAULT_PREFIX = "."

class RilowBot(commands.Bot):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

        self.config = Config("config.json")
        self.lang = Lang()

        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=self._get_prefix, 
            intents=intents
        )
    
    def _get_prefix(self, bot: commands.Bot, message: discord.Message) -> str:
        return self.config.get("guild_data", {})\
                            .get(message.guild.id, {})\
                            .get("prefix", DEFAULT_PREFIX)
    

    async def on_ready(self) -> None:
        self._logger.info("Bot ready!")
        

if __name__ == "__main__":
    rlog.init_logging()

    bot = RilowBot()
    bot.run(TOKEN)
        