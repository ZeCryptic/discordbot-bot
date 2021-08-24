import discord
import datetime
from discord.ext import commands, tasks
from discord.ext.commands import MemberConverter

PREFIX = '!'
"""
Lage dict som holder mengde @ du har sendt, og average responsetimen din
Endre så den leita etter svar rett etter @ istede for en ny for loop    
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
        #converter = MemberConverter()

        members = ctx.guild.members
        for member in members:
            self.members_dict[member.id] = []

        for channel in messages_dict:

            for message in messages_dict[channel]['messages']:
                #print(messages_dict[channel]['messages'].index(message))
                if "<@!" in message["content"] and not message['content'].startswith(PREFIX):
                    start_of_at = message["content"].find("<@")
                    end_of_at = message["content"].find(">")
                    if str(message["content"][(start_of_at+3):end_of_at]) in str(self.members_dict.keys()):
                        #print(message["content"].count("<@!"))
                        print(message["content"][(start_of_at+3):end_of_at])
                        print(self.members_dict.keys())
                        #member = await converter.convert(ctx, message["author"][:-5])
                        await self.find_response(ctx, message["content"][(start_of_at+3):end_of_at], message["created_at"], messages_dict, messages_dict[channel]['messages'].index(message))
                elif "<@&" in message["content"] and not message['content'].startswith(PREFIX):
                    print("wtf")
                elif "<@" in message["content"] and not message['content'].startswith(PREFIX):
                    start_of_at = message["content"].find("<@")
                    end_of_at = message["content"].find(">")
                    if str(message["content"][(start_of_at + 2):end_of_at]) in str(self.members_dict.keys()):
                        print(message["content"][(start_of_at + 2):end_of_at])
                        print(self.members_dict.keys())
                        #member = await converter.convert(ctx, message["author"][:-5])
                        await self.find_response(ctx, message["content"][(start_of_at+2):end_of_at], message["created_at"], messages_dict, messages_dict[channel]['messages'].index(message))

        await ctx.send("Update complete")



    async def find_response(self, ctx, member_id, time_sent, messages_dict, index):
        converter = MemberConverter()
        for channel in messages_dict:
            for message in messages_dict[channel]['messages'][(1+index):]:
                #print("heyo, this is second" ,messages_dict[channel]['messages'].index(message), "this is",index)
                member = await converter.convert(ctx, message["author"][:-5])
                if int(member.id) == int(member_id):
                    if time_sent < message["created_at"]:
                        difference = message["created_at"] - time_sent
                        self.members_dict[int(member_id)].append(difference)
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
