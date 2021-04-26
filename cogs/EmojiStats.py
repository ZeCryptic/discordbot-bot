import discord
from discord.ext import commands
from discord.ext.commands.errors import EmojiNotFound
from utils import format_filename
import pickle
import emoji

EMOJIES = emoji.UNICODE_EMOJI_ENGLISH
PREFIX = '!'


class EmojiStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_messages(self, guild_id):
        history = self.bot.get_cog('History')
        return history.load_messages(guild_id)

    @commands.command()
    async def usage(self, ctx, emote):

        is_emoji = False
        if emote in EMOJIES:
            is_emoji = True
            emote_name = emoji.demojize(emote).split(':')[1]
            emote_url = None
        else:
            emote = await commands.EmojiConverter().convert(ctx, emote)
            emote_url = emote.url
            emote_name = emote.name
            emote = str(emote.id)

        messages_dict = self.load_messages(ctx.guild.id)
        user_emote_usage = {}
        for user in ctx.guild.members:
            user_name = f'{user.name}#{user.discriminator}'
            user_emote_usage[user_name] = 0

        total_count = 0
        for channel in messages_dict:
            for message in messages_dict[channel]['messages']:
                if emote in message['emojis'] and not message['content'].startswith(PREFIX):
                    user_emote_usage[message['author']] += 1
                    total_count += 1

        medals = {0: '🥇', 1: '🥈', 2: '🥉'}
        embed = discord.Embed(title=f'"{emote_name}" has been used {total_count} total times:')
        if is_emoji:
            embed.set_thumbnail(url=f'https://emoji.beeimg.com/{emote}')
        else:
            embed.set_thumbnail(url=emote_url)
        for i, user in enumerate(sorted(user_emote_usage, key=user_emote_usage.get, reverse=True)):
            if i > 9 or user_emote_usage[user] <= 0:
                break
            embed.add_field(
                name=f'#{i + 1}: {medals.get(i, "")}{user}',
                value=str(user_emote_usage[user]),
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
