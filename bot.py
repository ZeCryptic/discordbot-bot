import discord
import os
import utils
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


def main():
    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'), intents=intents)

    for cog in utils.get_cogs():
        bot.load_extension(cog)

    @bot.command()
    @commands.is_owner()
    async def dev(ctx, arg):
        """Dev commands only accessible by the bot owners"""
        command = arg.lower()

        # Updates the bot with the latest changes from github. Only works for updating cogs in runtime
        if command == 'update':
            await ctx.send('Pulling latest update from github...')
            stream = os.popen('git pull')
            output = stream.read()
            await ctx.send(output)

        # Restarts all cogs
        elif command == 'reload':
            embed = discord.Embed(
                title='Reloading cogs',
                timestamp=ctx.message.created_at
            )
            for cog in utils.get_cogs():
                try:
                    bot.unload_extension(cog)
                    bot.load_extension(cog)
                    embed.add_field(
                        name=f'Reloaded: {cog}',
                        value='✅',
                        inline=False)

                except Exception as e:
                    embed.add_field(
                        name=f'Failed to reload: {cog}',
                        value=f'❌: {e}',
                        inline=False)

            await ctx.send(embed=embed)

    @bot.event
    async def on_ready():
        print(f'Bot logged in as {bot.user}')

    bot.run(TOKEN)


if __name__ == '__main__':
    main()
