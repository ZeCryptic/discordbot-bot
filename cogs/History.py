from discord.ext import commands
import discord
from pathlib import Path
import os
import _pickle as pickle
from emoji import get_emoji_regexp
import re

EMOJI_REGEX = get_emoji_regexp()
EMOTE_REGEX = r"<:(?P<name>\w+):(?P<id>\d+)>"

"""
TODO:
    - Implement teardown function to ensure message history is properly saved when unloading cog

Data structure
    messages = {channel_1: {messages: [],
                            last_date: datetime.datetime}
                channel_2: ...
                channel_3: ...
                ...
                }
"""


def message_to_dict(message: discord.Message):
    emojis = re.findall(EMOJI_REGEX, message.content)
    emotes = re.findall(EMOTE_REGEX, message.content)
    emotes_ids = [e[1] for e in emotes if e is not None]
    d = {'content': message.content,
         'author': f'{message.author.name}#{message.author.discriminator}',
         'created_at': message.created_at,
         'emojis': emojis + emotes_ids
         }
    return d


class History(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.messages = []
        self.history_data_path = Path('cogs/History_data')
        self.on_load()


    def get_logfile_path(self, guild_id):
        return self.history_data_path / f'{guild_id}_logs.pkl'

    def save_messages(self, guild_id, messages_dict):
        path = self.get_logfile_path(guild_id)

        if not os.path.exists(self.history_data_path):
            os.makedirs(self.history_data_path)
        with open(path, 'wb') as f:
            pickle.dump(messages_dict, f)

    def load_messages(self, guild_id):
        path = self.get_logfile_path(guild_id)

        try:
            with open(path, 'rb') as f:
                messages = pickle.load(f)
        except FileNotFoundError:
            messages = {}

        return messages

    async def log_all_messages(self, guild_id, output_message=None, embed=None):
        guild = self.bot.get_guild(guild_id)
        messages_dict = self.load_messages(guild_id)

        for channel in guild.text_channels:
            try:
                messages_dict[channel.name]
            except KeyError:
                messages_dict[channel.name] = {'messages': [], 'last_date': channel.created_at}
            last_date = messages_dict[channel.name]['last_date']

            n_messages = 0
            async for message in channel.history(limit=None, oldest_first=True, after=last_date):
                if message.author.bot:
                    continue
                messages_dict[channel.name]['messages'].append(message_to_dict(message))
                messages_dict[channel.name]['last_date'] = message.created_at
                n_messages += 1

            if output_message is not None:
                embed.add_field(name=channel.name,
                                value=f'{n_messages} new messages since: \n {last_date.strftime("%m/%d/%Y, %H:%M:%S")}')
                await output_message.edit(embed=embed)

        self.save_messages(guild_id, messages_dict)

    def on_load(self):
        pass

    def cog_unload(self):
        pass

    @commands.group(help="Logs all messages in the discord server. Message log is used by other commands")
    async def log_messages(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title='Logging all new messages',
                                  timestamp=ctx.message.created_at
                                  )
            output_message = await ctx.send(embed=embed)
            await self.log_all_messages(ctx.guild.id, output_message, embed)

    @log_messages.command(help="Deletes the message log file of this server. Only accessible by bot owners")
    @commands.is_owner()
    async def delete(self, ctx):
        path = self.get_logfile_path(ctx.guild.id)
        size = os.path.getsize(path)
        os.remove(path)
        await ctx.send(f'Deleting log file {path} ({size})')


def setup(bot):
    bot.add_cog(History(bot))
