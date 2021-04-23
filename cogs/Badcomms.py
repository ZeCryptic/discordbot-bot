import json
import discord
import os.path
import datetime
from discord.ext import commands, tasks
from pathlib import Path
"""
Do next
Improve help
Add see next vote to a command and maybe the leaderboard
Add a timer or something to the vote, so voters dont need to be hard coded
Start working on the roles
Maybe remove self.cNames and only use self.comms.keys()
Change the timer to something other than an hour
"""

# noinspection PyGlobalUndefined
class Badcomms(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.comms = None
        self.cNames = []
        self.vote_servers = None
        self.comms_data_path = Path("cogs/Badcomms_data/comms.json")
        self.comms_data_path2 = Path("cogs/Badcomms_data/vote_servers.json")
        self.show_time.start()
        self.load_comms()
        self.load_vote_servers()

    def load_vote_servers(self):
        if os.path.isfile(self.comms_data_path2):
            with open(self.comms_data_path2, encoding='utf-8') as f:
                self.vote_servers = json.load(f)
        else:
            self.vote_servers = {}
            with open(self.comms_data_path2, "x", encoding='utf-8') as f:
                json.dump(self.vote_servers, f)

    def load_comms(self):
        if os.path.isfile(self.comms_data_path):
            with open(self.comms_data_path, encoding='utf-8') as f:
                self.comms = json.load(f)
        else:
            self.comms = {}
            with open(self.comms_data_path, "x", encoding='utf-8') as f:
                json.dump(self.comms, f)

        self.cNames = []
        for i in self.comms.keys():
            self.cNames.append(i)

    def save_servers(self):
        with open(self.comms_data_path2, "w", encoding='utf-8') as f:
            json.dump(self.vote_servers, f, indent=6)

    def save(self):
        with open(self.comms_data_path, "w", encoding='utf-8') as f:
            json.dump(self.comms, f, indent=6)

        self.cNames = []
        for i in self.comms.keys():
            self.cNames.append(i)

    def new_date(self, user_input=None):
        global date
        if user_input is None:
            day = int(date[8:10])
        else:
            day = int(user_input)
        if len(str(day)) < 2:
            day_str = "0" + str(day)
        else:
            day_str = str(day)
        if day <= int(date[8:10]):
            if int(date[5:7]) == 12:
                if int(date[3:4]) == 9:  # Only works until 2039
                    day = f"2030-01-{day_str}"
                else:
                    day = f"{int(date[0:4]) + 1}-01-{day_str}"
            else:
                if int(date[5:7]) + 1 >= 9:
                    day = f"{(date[0:4])}-{int(date[5:7]) + 1}-{day_str}"
                else:
                    day = f"{(date[0:4])}-0{int(date[5:7]) + 1}-{day_str}"

        else:
            if day <= 9:
                day = f"{(date[0:4])}-{date[5:7]}-{day_str}"
            else:
                day = f"{(date[0:4])}-{date[5:7]}-{day_str}"

        return day

    def count_remarks(self, person):
        x = 0
        for i in self.comms[person]:
            x = x + 1
        return x

    @commands.command(name='badcomms', help="Type '!badcomms help'")
    async def bad_comms(self, ctx, person=None, *, arg=None):
        global date
        if person is not None:

            if person.lower().capitalize() in self.cNames:
                if arg is not None:
                    self.comms[person.lower().capitalize()].append(arg)
                    self.save()
                    remarks = self.count_remarks(person.lower().capitalize())
                    await ctx.send(
                        f"{str(ctx.author.display_name)} gave {person.lower().capitalize()} an remark and now has {remarks} remarks")
                else:
                    myEmbed = discord.Embed(
                        title=f"{str(ctx.author.display_name)} requested badcomms from: {person.lower().capitalize()}",
                        color=0x00ff00)
                    x = 0
                    for i in self.comms[person.lower().capitalize()]:
                        myEmbed.add_field(name=f"Badcomms nr: {x}", value=i, inline=False)
                        x = x + 1
                    await ctx.send(embed=myEmbed)

            elif person.lower() == "del":
                if arg is not None:
                    text_list = arg.split(" ")
                    if len(text_list) == 2:
                        name = text_list[0].lower().capitalize()
                        if name in self.cNames:
                            index = int(text_list[1])
                            if self.comms[name] != [] and len(self.comms[name]) - 1 >= index:
                                await ctx.send(
                                    f"{str(ctx.author.display_name)} removed remark from: {name} '{self.comms[name].pop(index)}'")
                                self.save()
                            else:
                                await ctx.send(f"{str(ctx.author.display_name)} that remark does not exist")

            elif person.lower() == "add":
                if arg is not None:
                    text_list = arg.split(" ")
                    if len(text_list) == 1:
                        name = text_list[0].lower().capitalize()
                        if name not in self.cNames:
                            self.comms[name] = []
                            await ctx.send(f"{str(ctx.author.display_name)} added: {name}")
                            self.save()

            elif person.lower() == "delete":
                if arg is not None:
                    text_list = arg.split(" ")
                    if len(text_list) == 1:
                        name = text_list[0].lower().capitalize()
                        if name in self.cNames:
                            await ctx.send(f"{str(ctx.author.display_name)} deleted: {name}")
                            self.comms.pop(name)
                            self.save()

            elif person.lower() == "leaderboard":
                myEmbed = discord.Embed(title=f"{str(ctx.author.display_name)} requested badcommers leaderboard",
                                        color=0x00ff00)
                x = 0

                for person in self.comms:
                    z = self.count_remarks(person)
                    myEmbed.add_field(name=f"{x} {person}", value=f"Number of badcomms: {z}", inline=False)
                    x = x + 1

                await ctx.send(embed=myEmbed)

            elif person.lower() == "vote": #Need to write a command to show when next vote is due
                if arg is not None:
                    text_list = arg.split(" ")
                    if len(text_list) == 1:
                        try:
                            day = int(text_list[0])
                            self.new_date(day)
                            self.vote_servers[ctx.guild.id] = [ctx.channel.id, day]
                            self.save_servers()
                        except:
                            await ctx.send("Needs the date of the vote, not the month, example '!badcomms vote 30' will vote on the 30 th of every month. PS. It will skip February")

            elif person.lower() == "help": #Need to rewrite help to show the new changes
                if arg is None:
                    myEmbed = discord.Embed(title=f"Helping {str(ctx.author.display_name)}", color=0x00ff00)
                    myEmbed.add_field(name="Add remarks", value="To add remarks type '!badcomms person remark'",
                                      inline=False)
                    myEmbed.add_field(name="Delete remarks",
                                      value="To delete remark type '!badcomms del person number'(The number is correlating to that persons list of remarks)",
                                      inline=False)
                    myEmbed.add_field(name="See remarks", value="To add remarks type '!badcomms person'", inline=False)
                    myEmbed.add_field(name="See leaderboard", value="To see leaderboard type '!badcomms leaderboard'",
                                      inline=False)
                    myEmbed.add_field(name="Vote badcomms",
                                      value="To vote on badcomms type '!badcomms leaderboard vote'", inline=False)
                    myEmbed.add_field(name="Add person", value="To add person type '!badcomms add person'",
                                      inline=False)
                    myEmbed.add_field(name="Delete person", value="To delete person type '!badcomms delete person'",
                                      inline=False)
                    await ctx.send(embed=myEmbed)
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        global voteList, vote0, vote1, vote2, vote3, vote4, vote5, vote6, vote7, vote8, votes, actualMessage
        if reaction.message == actualMessage:
            emoji = reaction.emoji
            ch = reaction.message.channel

            if user.bot:
                return
            else:
                if user not in voteList:
                    voteList.append(str(user))

                    if emoji == "0️⃣":
                        vote0 = vote0 + 1
                        votes["vote0"] = vote0

                    elif emoji == "1️⃣":
                        vote1 = vote1 + 1
                        votes["vote1"] = vote1

                    elif emoji == "2️⃣":
                        vote2 = vote2 + 1
                        votes["vote2"] = vote2

                    elif emoji == "3️⃣":
                        vote3 = vote3 + 1
                        votes["vote3"] = vote3

                    elif emoji == "4️⃣":
                        vote4 = vote4 + 1
                        votes["vote4"] = vote4

                    elif emoji == "5️⃣":
                        vote5 = vote5 + 1
                        votes["vote5"] = vote5

                    elif emoji == "6️⃣":
                        vote6 = vote6 + 1
                        votes["vote6"] = vote6

                    elif emoji == "7️⃣":
                        vote7 = vote7 + 1
                        votes["vote7"] = vote7

                    elif emoji == "8️⃣":
                        vote8 = vote8 + 1
                        votes["vote8"] = vote8

                    else:
                        return

                if len(voteList) == 7:
                    x = -1
                    who = ""
                    for y, i in votes.items():
                        if i > x:
                            x = i
                            who = y
                    index = int(who[4])
                    await ch.send(f"{self.cNames[index]} has the most votes({x}) for bad comms")

    async def leaderboard_vote(self):
        for x, y in self.vote_servers.items():
            channel = self.bot.get_guild(int(x)).get_channel(int(y[0]))

            myEmbed = discord.Embed(title=f"Its time for the badcommers vote",
                                    color=0x00ff00)
            x = 0

            for person in self.comms:
                z = self.count_remarks(person)
                myEmbed.add_field(name=f"{x} {person}", value=f"Number of badcomms: {z}", inline=False)
                x = x + 1
            message = await channel.send(embed=myEmbed)
            emojis = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
            global voteList, vote0, vote1, vote2, vote3, vote4, vote5, vote6, vote7, vote8, votes, actualMessage
            actualMessage = message
            voteList = []
            votes = {"vote0": 0, "vote1": 0, "vote2": 0, "vote3": 0, "vote4": 0, "vote5": 0, "vote6": 0,
                     "vote7": 0,
                     "vote8": 0}
            vote0 = 0
            vote1 = 0
            vote2 = 0
            vote3 = 0
            vote4 = 0
            vote5 = 0
            vote6 = 0
            vote7 = 0
            vote8 = 0

            for emoji in emojis[:x]:
                await message.add_reaction(emoji)

    @tasks.loop(hours=1)
    async def show_time(self):
        global date
        date = str(datetime.datetime.today())
        #date = str(datetime.date(2021, 4, 25)) #For testing
        for x, y in self.vote_servers.items():
            if str(y[1]) in date:
                await self.leaderboard_vote()
                self.vote_servers[x] = [y[0], self.new_date()]
                self.save_servers()

    @show_time.before_loop
    async def before_show_time(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Badcomms(bot))
