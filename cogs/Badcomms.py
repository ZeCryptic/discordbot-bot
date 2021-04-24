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
Maybe remove self.cNames and only use self.comms.keys()
Change the timer to something other than an hour
Make leaderboard display rank 1-9 in badcomms, others wont be available for voting
Also add names in the form that I can use them to give roles
Add a function to replace names if anybody switches gamertags
Add so each server can have their own badcomms files
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
            is_name = False
            is_name2 = False
            if arg is not None:
                text_list = arg.split(" ")
            for i in self.comms.keys():
                x = i.split("/")
                if person.lower().capitalize() in x[0]:
                    is_name = True
                    person = i
                if arg is not None:
                    name = text_list[0].lower().capitalize()
                    if name in x[0]:
                        name_id = i
                        is_name2 = True

            if is_name is True:
                if arg is not None:

                    self.comms[person].append(arg)
                    self.save()
                    remarks = self.count_remarks(person)
                    await ctx.send(
                        f"{str(ctx.author.display_name)} gave {person.split('/')[0]} an remark because '{arg}', and now has {remarks} remarks.")
                else:
                    myEmbed = discord.Embed(
                        title=f"{str(ctx.author.display_name)} requested badcomms from: {person}",
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
                        if is_name2 is True:
                            try:
                                index = int(text_list[1])
                                if self.comms[name] != [] and len(self.comms[name]) - 1 >= index:
                                    await ctx.send(
                                        f"{str(ctx.author.display_name)} removed remark from: {name.split('/')[0]} '{self.comms[name].pop(index)}'")
                                    self.save()
                                else:
                                    await ctx.send(f"{str(ctx.author.display_name)} that remark does not exist")
                            except:
                                await ctx.send("No number detected")

            elif person.lower() == "add":
                parameter = True
                if arg is not None:
                    if len(text_list) == 2:
                        name = text_list[0].lower().capitalize()
                        id = text_list[1][3:-1]
                        for i in self.cNames:
                            x = i.split("/")
                            if name == x[0]:
                                parameter = False
                            elif id == x[1]:
                                parameter = False
                        if parameter == True:
                            if text_list[1][:3] == "<@!":
                                namep = f"{name}/{text_list[1][3:-1]}"
                                self.comms[namep] = []
                                await ctx.send(f"{ctx.author.display_name} added: {name}")
                                self.save()

            elif person.lower() == "delete":
                if arg is not None:
                    if len(text_list) == 1:
                        if is_name2 is True:
                            await ctx.send(f"{str(ctx.author.display_name)} deleted: {name}")
                            self.comms.pop(name_id)
                            self.save()

            elif person.lower() == "leaderboard":
                myEmbed = discord.Embed(title=f"{str(ctx.author.display_name)} requested badcommers leaderboard",
                                        color=0x00ff00)
                x = 0

                for person in self.comms:
                    z = self.count_remarks(person)
                    myEmbed.add_field(name=f"{x} {person.split('/')[0]}", value=f"Number of badcomms: {z}", inline=False)
                    x = x + 1

                await ctx.send(embed=myEmbed)

            elif person.lower() == "vote": #Need to write a command to show when next vote is due
                if arg is not None:
                    if len(text_list) == 5:
                        try:
                            print(text_list[2])
                            day = int(text_list[0])
                            hours = int(text_list[1])
                            self.vote_servers[ctx.guild.id] = [ctx.channel.id, self.new_date(day), False, hours, hours, int(text_list[2][3:-1]), int(text_list[3][3:-1]), int(text_list[4][3:-1])]
                            self.save_servers()
                        except:
                            await ctx.send("Needs the date of the vote, not the month, example '!badcomms vote 30' will vote on the 30 th of every month. PS. It will skip February")

            elif person.lower() == "test":
                for x, y in self.vote_servers.items():
                    await self.leaderboard_vote(x,y)
                    self.vote_servers[x] = [y[0], y[1], True, y[3], y[4], y[5], y[6], y[7]]

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
        global voteList, vote0, vote1, vote2, vote3, vote4, vote5, vote6, vote7, vote8, vote9, votes, actualMessage
        if reaction.message == actualMessage:
            emoji = reaction.emoji

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

                    elif emoji == "9️⃣":
                        vote9 = vote9 + 1
                        votes["vote9"] = vote9

                    else:
                        return

    async def count_votes(self, x, content):
        global voteList, vote0, vote1, vote2, vote3, vote4, vote5, vote6, vote7, vote8, vote9, votes, actualMessage, voteable
        first = ""
        second = ""
        third = ""
        liste = []
        first_done = False
        second_done = False
        third_done = False
        for y in sorted(votes.values())[::-1]:
            liste.append(y)

        for y, i in votes.items():
            if i == liste[0] and first_done is not True:
                first = y
                first_done = True
            elif i == liste[1] and second_done is not True:
                second = y
                second_done = True
            elif i == liste[2] and third_done is not True:
                third = y
                third_done = True

        first_index = int(first[4])
        if second != "":
            second_index = int(second[4])
        else:
            second_index = -1
        if third != "":
            third_index = int(third[4])
        else:
            third_index = -1
        count = 0
        for name_id, number_of_badcomms in voteable.items():
            if first_index == count:
                await self.give_role(x, content, name_id, number_of_badcomms, first, 1)
                count = count + 1
            elif second_index == count:
                await self.give_role(x, content, name_id, number_of_badcomms, second, 2)
                count = count + 1
            elif third_index == count:
                await self.give_role(x, content, name_id, number_of_badcomms, third, 3)
                count = count + 1
            else:
                count = count + 1

    async def give_role(self, x, content, name_id, number_of_badcomms, number_votes, place):
        global votes
        channel = self.bot.get_guild(int(x)).get_channel(int(content[0]))
        role_ids = [int(content[5]), int(content[6]), int(content[7])]
        for role in [r for r in self.bot.get_guild(int(x)).roles if r.id == role_ids[place-1]]:
            try:
                await channel.send(f"{name_id.split('/')[0]} has been placed {place} with votes({votes[number_votes]}) and badcomms({number_of_badcomms}), and is therefore granted the role '{role}' for bad comms")
                await self.bot.get_guild(int(x)).get_member(int(name_id.split("/")[1])).add_roles(role)
            except:
                return

    async def leaderboard_vote(self, x, y):
        global voteable
        channel = self.bot.get_guild(int(x)).get_channel(int(y[0]))

        myEmbed = discord.Embed(title=f"Its time for the badcommers vote",
                                color=0x00ff00)
        x = 0
        z = {}
        voteable = {}
        for person in self.comms:
            z[person] = self.count_remarks(person)

        order = sorted(z.values())

        for i in order[::-1]:
            for a, y in z.items():
                if i == y:
                    if x < 10:
                        if a not in voteable.keys():
                            voteable[a] = y
                            myEmbed.add_field(name=f"{x} {a.split('/')[0]}", value=f"Number of badcomms: {y}", inline=False)
                            x = x + 1

        message = await channel.send(embed=myEmbed)
        emojis = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        global voteList, vote0, vote1, vote2, vote3, vote4, vote5, vote6, vote7, vote8, vote9, votes, actualMessage
        actualMessage = message
        voteList = []
        votes = {"vote0": 0, "vote1": 0, "vote2": 0, "vote3": 0, "vote4": 0, "vote5": 0, "vote6": 0,
                 "vote7": 0,
                 "vote8": 0, "vote9": 0}
        vote0 = 0
        vote1 = 0
        vote2 = 0
        vote3 = 0
        vote4 = 0
        vote5 = 0
        vote6 = 0
        vote7 = 0
        vote8 = 0
        vote9 = 0

        for emoji in emojis[:x]:
            await message.add_reaction(emoji)

    @tasks.loop(hours=1)
    async def show_time(self):
        global date
        date = str(datetime.datetime.today())
        #date = str(datetime.date(2021, 4, 25)) #For testing
        for x, y in self.vote_servers.items():
            if str(y[1]) in date:
                await self.leaderboard_vote(x, y)
                self.vote_servers[x] = [y[0], self.new_date(), True, y[3], y[4], y[5], y[6], y[7]]
                self.save_servers()
            if y[2] is True:
                if y[3] >= 1:
                    self.vote_servers[x] = [y[0], y[1], True, y[3]-1, y[4], y[5], y[6], y[7]]
                    self.save_servers()
                elif y[3] == 0:
                    self.vote_servers[x] = [y[0], y[1], False, y[4], y[4], y[5], y[6], y[7]]
                    self.save_servers()
                    await self.count_votes(x, y)

    @show_time.before_loop
    async def before_show_time(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Badcomms(bot))
