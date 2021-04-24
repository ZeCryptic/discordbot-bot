import discord
from discord.ext import commands
from discord.ext.commands.errors import EmojiNotFound
from utils import format_filename
import pickle
import re

EMOJI_REGEX = r"<:(?P<name>\w+):(?P<id>\d+)>"
PREFIX = '!'    # TODO: Make prefix a variable configurable by the user


class EmojiStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_messages(self, guild_id):
        history = self.bot.get_cog('History')
        return history.load_messages(guild_id)

    def extract_emote_ids(self, message):
        emojis = re.findall(EMOJI_REGEX, message)
        ids = [e[1] for e in emojis if e is not None]
        return ids

    @commands.command()
    async def usage(self, ctx, emoji: discord.Emoji):
        messages_dict = self.load_messages(ctx.guild.id)

        user_emoji_usage = {}
        for user in ctx.guild.members:
            user_name = f'{user.name}#{user.discriminator}'
            user_emoji_usage[user_name] = 0

        total_count = 0
        for channel in messages_dict:
            for message in messages_dict[channel]['messages']:
                if str(emoji.id) in self.extract_emote_ids(message['content']) and not message['content'].startswith(PREFIX):
                    user_emoji_usage[message['author']] += 1
                    total_count += 1

        medals = {0: '🥇', 1: '🥈', 2: '🥉'}
        embed = discord.Embed(title=f'Usage of the {emoji} emote:')
        for i, user in enumerate(sorted(user_emoji_usage, key=user_emoji_usage.get, reverse=True)):
            if i > 9 or user_emoji_usage[user] <= 0:
                break
            embed.add_field(
                name=f'#{i+1}: {medals.get(i, "")}{user}',
                value=str(user_emoji_usage[user]),
                inline=False
            )

        await ctx.send(embed=embed)

    @usage.error
    async def usage_error(self, ctx, error):
        if isinstance(error, EmojiNotFound):
            await ctx.send('Emoji not found. You can only use emojis from this server')
        else:
            print(error)
            await ctx.send(f'Error: {error}')



def setup(bot):
    bot.add_cog(EmojiStats(bot))
