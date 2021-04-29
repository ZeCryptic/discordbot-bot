import discord
from discord.ext import commands
from discord.ext.commands.errors import EmojiNotFound
import emoji

EMOJIES = emoji.UNICODE_EMOJI_ENGLISH
PREFIX = '!'


class EmojiStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_messages(self, guild_id):
        history = self.bot.get_cog('History')
        return history.load_messages(guild_id)

    def _displayable_emote(self, emote):
        if str.isdigit(emote):
            id = int(emote)
            custom_emote = self.bot.get_emoji(id)
            if custom_emote is None:
                emote_name = 'DELETED_EMOTE'
                emote = '𖡄'
            else:
                emote_name = custom_emote.name
                emote = f'<:{emote_name}:{id}>'
        else:
            emote_name = emoji.demojize(emote).replace(':', '')

        return f'{emote_name} {emote}'

    def _create_leaderboard_embed(self, usage_dict, title, image_url=None):
        medals = {0: '🥇', 1: '🥈', 2: '🥉'}
        embed = discord.Embed(title=title)
        embed.set_thumbnail(url=image_url)
        for i, key in enumerate(sorted(usage_dict, key=usage_dict.get, reverse=True)):
            if i > 9 or usage_dict[key] <= 0:
                break
            embed.add_field(
                name=f'#{i + 1}: {medals.get(i, "")}{key}',
                value=str(usage_dict[key]),
                inline=False
            )

        return embed

    def _find_user_usage(self, ctx, user, all_users=False):
        messages_dict = self.load_messages(ctx.guild.id)
        user_name = f'{user.name}#{user.discriminator}'
        emote_usage = {}

        total_count = 0
        for channel in messages_dict:
            for message in messages_dict[channel]['messages']:
                if (message['author'] == user_name and not message['content'].startswith(PREFIX)) or all_users:
                    for emote in message['emojis']:
                        emote_usage[emote] = emote_usage.get(emote, 0) + 1
                        total_count += 1

        return emote_usage, total_count

    def _find_emote_usage(self, ctx, emote):
        messages_dict = self.load_messages(ctx.guild.id)
        user_emote_usage = {}

        total_count = 0
        for channel in messages_dict:
            for message in messages_dict[channel]['messages']:
                if emote in message['emojis'] and not message['content'].startswith(PREFIX):
                    user_emote_usage[message['author']] = user_emote_usage.get(message['author'], 0) + 1
                    total_count += 1

        return user_emote_usage, total_count

    @commands.command()
    async def usage(self, ctx, arg):
        user = ctx.guild.get_member_named(arg)
        is_user = False
        emote_name = None
        emote = None
        all_users = False
        user_name = ''

        if arg.lower() == 'all':
            is_user = True
            all_users = True
            leaderboard_thumbnail = ctx.guild.icon_url
            user = ctx.message.author
            user_name = ctx.guild.name
        elif user is not None:
            is_user = True
            leaderboard_thumbnail = user.avatar_url
            user_name = user.name
        elif arg in EMOJIES:
            emote = arg
            emote_name = emoji.demojize(emote).split(':')[1]
            leaderboard_thumbnail = f'https://emoji.beeimg.com/{emote}'
        else:
            emote = await commands.EmojiConverter().convert(ctx, arg)
            leaderboard_thumbnail = emote.url
            emote_name = emote.name
            emote = str(emote.id)

        if is_user:
            _usage, usage_count = self._find_user_usage(ctx, user, all_users)
            usage = {}
            for key in _usage.keys():
                new_key = self._displayable_emote(key)
                usage[new_key] = _usage[key]
            title = f'"{user_name}" has used {usage_count} total emotes:'
        else:
            usage, usage_count = self._find_emote_usage(ctx, emote)
            title = f'"{emote_name}" has been used {usage_count} total times:'

        embed = self._create_leaderboard_embed(usage, title, leaderboard_thumbnail)

        await ctx.send(embed=embed)

    @usage.error
    async def usage_error(self, ctx, error):
        if isinstance(error, EmojiNotFound):
            await ctx.send('Emoji or user not found. You can only use emojis or users from this server')
        else:
            print(error)
            await ctx.send(f'Error: {error}')


def setup(bot):
    bot.add_cog(EmojiStats(bot))
