from discord.ext import commands
from random import randint, sample
import datetime
import typing


class Basics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Rolls a number between  0 and a specified number (defaults to 100)')
    async def roll(self, ctx, max_roll: typing.Optional[int] = 100):
        if max_roll >= 0:
            await ctx.send(f'{ctx.message.author.mention} rolled a **{randint(0, max_roll)}**')
        else:
            await ctx.send(f'You can only roll for positive numbers')

    @commands.command(help='Posts a random ordering of the arguments')
    async def order(self, ctx, *args):
        if not args:
            await ctx.send('No arguments given.')
            return
        out = [f'**{i + 1}**: {element}\n' for i, element in enumerate(sample(args, k=len(args)))]
        await ctx.send(''.join(out))

    @commands.command(help='Posts a random ordering of the users in voice chat')
    async def ordervoice(self, ctx):
        if not ctx.author.voice:
            await ctx.send('You need to be in a voice channel to use this command')
            return
        voice_members = [f'{member.nick} ({member.name})' for member in ctx.author.voice.channel.members]
        out = [f'**{i + 1}**: {element}\n' for i, element in enumerate(sample(voice_members, k=len(voice_members)))]
        await ctx.send(''.join(out))

    @commands.command(help='The bot responds with "Pong!" and the response latency')
    async def ping(self, ctx):
        time_delta = datetime.datetime.now() - ctx.message.created_at
        await ctx.send(f'Pong! `({time_delta.microseconds * 2 // 1000} ms)`')


def setup(bot):
    bot.add_cog(Basics(bot))
