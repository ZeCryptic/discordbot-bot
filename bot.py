import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


def main():
    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

    @bot.command()
    async def test(ctx):
        await ctx.send('test :)')

    @bot.event
    async def on_ready():
        print(f'Bot logged in as {bot.user}')

    bot.run(TOKEN)


if __name__ == '__main__':
    main()
