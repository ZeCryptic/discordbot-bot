import discord
from discord.ext import commands
from utils import format_filename
import pickle
import re


class EmojiStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.messages = {}

    @commands.command()
    async def emoji(self, ctx):
        await ctx.send('Scanning all channels for emoji usage. This might take a while...')
        user_usage, overall_usage = await self.get_emoji_usage(ctx)
        response_string = '>>> '
        for i, e_id in enumerate(sorted(overall_usage, key=overall_usage.get, reverse=False)):
            if i >= 10:
                break
            response_string += f'**#{i + 1}**: {self.bot.get_emoji(e_id)}, {overall_usage[e_id]}\n'

        await ctx.send(response_string)
        filename = format_filename(ctx.guild.name)
        pickle.dump(user_usage, open(f'EmojiStats_data\\{filename}_uu.pkl', 'wb'))
        pickle.dump(overall_usage, open(f'EmojiStats_data\\{filename}_ou.pkl', 'wb'))

    def get_emoji_name(self, emoji_id):
        return self.bot.get_emoji(emoji_id).name


    @staticmethod
    async def get_emoji_usage(ctx):
        channels = ctx.guild.channels
        # channels = [ctx.channel] TESTING

        # initializes dictionaries, TODO: simplify the initialization
        channel_users = [f'{m.name}#{m.discriminator}' for m in ctx.guild.members if not m.bot]
        channel_emoji_ids = [e.id for e in ctx.guild.emojis]
        user_usage_dict = {}
        emojies_dict = {}
        for e_id in channel_emoji_ids:
            emojies_dict[e_id] = 0
        for user in channel_users:
            user_usage_dict[user] = emojies_dict.copy()
        for channel in channels:
            if type(channel) != discord.TextChannel:
                continue

            async for message in channel.history(limit=None):
                if message.author.bot:
                    continue

                message_emojies = re.findall("<:[^<,>]+:[0-9]+>", message.content)
                if not message_emojies:
                    continue

                author = f'{message.author.name}#{message.author.discriminator}'
                for emoji in message_emojies:
                    id = int(emoji.split(':')[2][:-1])
                    if id not in channel_emoji_ids:  # Emoji likely not from server or deleted
                        continue
                    user_usage_dict[author][id] += 1
                    emojies_dict[id] += 1

        return user_usage_dict, emojies_dict

