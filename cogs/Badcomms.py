import discord
import datetime
from discord.ext import commands, tasks
from discord.ext.commands import MemberConverter

PREFIX = "!"
"""
Lage dict som holder mengde @ du har sendt, og average responsetimen din

"""

# noinspection PyGlobalUndefined
class Badcomms(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.members_dict = {}
    def load_messages(self, guild_id):
        history = self.bot.get_cog("History")
        return history.load_messages(guild_id)

    @commands.command(name="update")
    @commands.is_owner()
    async def _find_user_ats(self, ctx):

        messages_dict = self.load_messages(ctx.guild.id)

        converter = MemberConverter()

        members = ctx.guild.members
        for member in members:
            self.members_dict[member.id] = []
        for channel in messages_dict:
            for message in messages_dict[channel]['messages']:
                if "@" in message["content"] and not message['content'].startswith(PREFIX):
                    member = await converter.convert(ctx, message["author"])
                    await self.find_response(ctx, member.id, message["created_at"], messages_dict)



    async def find_response(self, ctx, member_id, time_sent, messages_dict):
        converter = MemberConverter()
        for channel in messages_dict:
            for message in messages_dict[channel]['messages']:
                member = await converter.convert(ctx, message["author"])
                if member.id == member_id:
                    if time_sent < message["created_at"]:
                        #print(time_sent, message["created_at"])
                        #print("Hei der")
                        difference = message["created_at"] - time_sent
                        self.members_dict[member_id].append(difference)
                        return

    @commands.command(name='find')
    @commands.is_owner()
    async def find_average_responsetime(self, ctx, member_id=None):
        converter = MemberConverter()
        if member_id is None:
            member_id = str(ctx.author.id)
        count = 0
        first = True
        for member, response_times in self.members_dict.items():
            if str(member) in member_id:
                for response_time in response_times:
                    if first is True:
                        average = response_time
                        count += 1
                        first = False
                    else:
                        count += 1
                        average += response_time
                average = average/count
                tagged = await converter.convert(ctx, member_id)
        await ctx.send(f"The average response time for {tagged.name} is {average}")


def setup(bot):
    bot.add_cog(Badcomms(bot))
