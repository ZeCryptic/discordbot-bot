from discord.ext import commands


class TemplateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def template(self, ctx):
        await ctx.send('this is a template command :))')


def setup(bot):
    bot.add_cog(TemplateCog(bot))
