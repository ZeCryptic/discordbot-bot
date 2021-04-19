import discord
from discord.ext import commands


def main():

    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)

    @bot.command()
    async def test(ctx):
        await ctx.send('test :)')

    @bot.event
    async def on_ready():
        print(f'Bot logged in as {bot.user}')

    with open('token', 'r') as f:
        token = f.read()

    bot.run(token)

if __name__ == '__main__':
    main()