from discord.ext import commands


class Configs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def config(self, ctx):
        await ctx.send('Nothing implemented yet')


def setup(bot):
    bot.add_cog(Configs(bot))
