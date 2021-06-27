import os

import discord
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded
from discord.ext.commands.errors import NotOwner

import utils


class Configs(commands.Cog):
    """Commands used to configure the bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(help="Dev commands only accessible to owners")
    @commands.is_owner()
    async def dev(self, ctx):
        """Dev commands only accessible by the bot owners"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid sub command')

    @dev.command(help="Calls github pull to update the bot")
    async def update(self, ctx):
        await ctx.send('Pulling latest update from github...')
        stream = os.popen('git pull')
        output = stream.read()
        await ctx.send(output)

    @dev.command(help="Reloads all cogs in cogs/")
    async def reload(self, ctx):
        embed = discord.Embed(
            title='Reloading cogs',
            timestamp=ctx.message.created_at
        )
        for cog in utils.get_cogs():
            try:
                self.bot.unload_extension(cog)
            except ExtensionNotLoaded:
                pass
            try:
                self.bot.load_extension(cog)
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

    @dev.command(help="Installs all dependencies in requirements.txt")
    async def install(self, ctx):
        stream = os.popen('python3 -m pip install -r requirements.txt')
        output = stream.read()
        await ctx.send(output)

    @dev.error
    async def dev_error(self, ctx, error):
        if isinstance(error, NotOwner):
            await ctx.send('Dev commands are only usable by bot owners')
        else:
            await ctx.send('There was an error executing that command. Check the console')
            print('Error')


def setup(bot):
    bot.add_cog(Configs(bot))
