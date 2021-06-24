import discord
import os

from discord.ext.commands import ExtensionNotLoaded, ExtensionNotFound

import utils
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = '!' # TODO: Make prefix a variable configurable by the user


def main():
    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), intents=intents, case_insensitive=True)

    for cog in utils.get_cogs():
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f'Error loading cog "{cog}": {e}')

    @bot.event
    async def on_ready():
        print(f'Bot logged in as {bot.user}')

    bot.run(TOKEN)


if __name__ == '__main__':
    main()
