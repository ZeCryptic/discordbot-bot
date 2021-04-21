import os

import discord
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

import utils


class Configs(commands.Cog):
    """Commands used to configure the bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def dev(self, ctx, arg):
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


def setup(bot):
    bot.add_cog(Configs(bot))
