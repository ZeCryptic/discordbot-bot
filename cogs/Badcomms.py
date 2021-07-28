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
    async def _find_user_ats(self, ctx):

        messages_dict = self.load_messages(ctx.guild.id)

        converter = MemberConverter()

        members = ctx.guild.members
        for member in members:
            self.members_dict[member.id] = []
        print(self.members_dict)
        for channel in messages_dict:
            for message in messages_dict[channel]['messages']:
                if "@" in message["content"] and not message['content'].startswith(PREFIX):
                    #print(message["content"])
                    #print(message["created_at"])
                    #print(type(message["created_at"]))
                    member = await converter.convert(ctx, message["author"])
                    await self.find_response(ctx, member.id, message["created_at"], messages_dict)
                    #Send videre til å finne responsen


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
                        print("hello there", difference)
                        return

    async def find_average_responsetime(self, ctx, member_id, response_time):
        for member, average in self.members_dict.items():
            if member == member_id:

        print(self.members_dict)


def setup(bot):
    bot.add_cog(Badcomms(bot))
