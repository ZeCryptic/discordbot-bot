from discord.ext import commands
import discord
from pathlib import Path
import datetime
import os
import _pickle as pickle
import sys

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
    d = {'content': message.content,
         'author': f'{message.author.name}#{message.author.discriminator}',
         'created_at': message.created_at
         }
    return d


class History(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.messages = []
        self.history_data_path = Path('cogs/History_data')
        self.on_load()

    def save_messages(self, guild_id, messages_dict):
        path = self.history_data_path / f'{guild_id}_logs.pkl'

        if not os.path.exists(self.history_data_path):
            os.makedirs(self.history_data_path)
        with open(path, 'wb') as f:
            pickle.dump(messages_dict, f)

    def load_messages(self, guild_id):
        path = self.history_data_path / f'{guild_id}_logs.pkl'

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

    @commands.command()
    async def log_messages(self, ctx):
        embed = discord.Embed(title='Logging all new messages',
                              timestamp=ctx.message.created_at
                              )
        output_message = await ctx.send(embed=embed)
        await self.log_all_messages(ctx.guild.id, output_message, embed)


def setup(bot):
    bot.add_cog(History(bot))
