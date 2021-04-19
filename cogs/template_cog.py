from discord.ext import commands


class TemplateCog(commands.cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command
    async def template(self, ctx):
        await ctx.send('this is a template command :))')