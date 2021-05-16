import json
import discord
import os.path
import datetime
from discord.ext import commands, tasks
from pathlib import Path

"""
Do next
Make the vote function work better with weird dates
Make the vote show correlating emojis
"""


# noinspection PyGlobalUndefined
class Badcomms(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.comms = None
        self.vote_servers = None
        self.comms_data_path2 = Path("cogs/Badcomms_data/vote_servers.json")
        self.comms_data_path = Path("cogs/Badcomms_data")
        self.show_time.start()
        self.load_vote_servers()

    def get_file_path(self, guild_id):
        return self.comms_data_path / f"{guild_id}_comms.json"

    def load_vote_servers(self):
        if os.path.isfile(self.comms_data_path2):
            with open(self.comms_data_path2, encoding='utf-8') as f:
                self.vote_servers = json.load(f)
        else:
            self.vote_servers = {}
            with open(self.comms_data_path2, "x", encoding='utf-8') as f:
                json.dump(self.vote_servers, f)

    def load_comms(self, guild_id):
        path = self.get_file_path(guild_id)

        if not os.path.exists(self.comms_data_path):
            os.makedirs(self.comms_data_path)
        if os.path.isfile(path):
            with open(path, encoding='utf-8') as f:
                self.comms = json.load(f)
        else:
            self.comms = {}
            with open(path, "x", encoding='utf-8') as f:
                json.dump(self.comms, f)

    def save_servers(self):
        with open(self.comms_data_path2, "w", encoding='utf-8') as f:
            json.dump(self.vote_servers, f, indent=6)

    def save(self, guild_id):
        path = self.get_file_path(guild_id)

        if not os.path.exists(self.comms_data_path):
            os.makedirs(self.comms_data_path)
        with open(path, "w", encoding='utf-8') as f:
            json.dump(self.comms, f, indent=6)

    @staticmethod
    def new_date(user_input=None):
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
        return len(self.comms[person])

    def remove_remarks(self, guild_id):
        self.load_comms(guild_id)
        for name in self.comms.keys():
            self.comms[name] = []
        self.save(guild_id)

    def is_name_in_dict(self, name):
        name = name.lower().capitalize()
        for name_id in self.comms.keys():
            name_in_list = name_id.split("/")
            if name_in_list[0] == name:
                return True, name_id, name
        return False, name

    @commands.group(name='badcomms', help="Type '!badcomms'")
    async def badcomms(self, ctx):
        self.load_comms(ctx.guild.id)
        if ctx.invoked_subcommand is None:
            my_embed = discord.Embed(title=f"Helping {str(ctx.author.display_name)}", color=0x00ff00)
            my_embed.add_field(name="Add remarks", value="To add remarks type '!badcomms remark [name] [reason]'",
                               inline=False)
            my_embed.add_field(name="Delete remarks",
                               value="To delete remark type '!badcomms del [name] [number]'(The number is correlating to "
                                     "that persons list of remarks)",
                               inline=False)
            my_embed.add_field(name="See remarks", value="To add remarks type '!badcomms show [name]'", inline=False)
            my_embed.add_field(name="See leaderboard", value="To see leaderboard type '!badcomms leaderboard'",
                               inline=False)
            my_embed.add_field(name="Add person", value="To add person type '!badcomms add [name] [@name]'",
                               inline=False)
            my_embed.add_field(name="Delete person", value="To delete person type '!badcomms delete [name]'",
                               inline=False)
            my_embed.add_field(name="Add vote",
                               value="To add a monthly vote type '!badcomms vote add [date] [hours] [@role1] [@role2] "
                                     "[@role3]'", inline=False)
            my_embed.add_field(name="Delete vote", value="To stop server from monthly votes type '!badcomms vote del'", inline=False)
            await ctx.send(embed=my_embed)

    @badcomms.command(name='del')
    async def delete_remark(self, ctx, name=None, index=None):
        """
        !badcomms del name index
        """
        if index is not None:
            is_name_and_name_id = self.is_name_in_dict(name)  # Returns True or False to [0], name_id to [1] and name to [3]
            if is_name_and_name_id[0] is True:
                try:
                    index = int(index)
                    if self.comms[is_name_and_name_id[1]] != [] and len(self.comms[is_name_and_name_id[1]]) - 1 >= index:
                        await ctx.send(
                            f"{str(ctx.author.display_name)} removed remark from: {is_name_and_name_id[2]} '{self.comms[is_name_and_name_id[1]].pop(index)}'")
                        self.save(ctx.guild.id)
                    else:
                        await ctx.send(f"{str(ctx.author.display_name)} that remark does not exist")
                except:
                    await ctx.send("No number detected")
                return

    @badcomms.command(name='delete')
    async def delete_name(self, ctx, name=None):
        """
        !badcomms delete name
        """
        if name is not None:
            is_name_and_name_id = self.is_name_in_dict(name)  # Returns True or False to [0], name_id to [1] and name to [3]
            if is_name_and_name_id[0] is True:
                await ctx.send(f"{str(ctx.author.display_name)} deleted: {is_name_and_name_id[2]}")
                self.comms.pop(is_name_and_name_id[1])
                self.save(ctx.guild.id)
                return

    @badcomms.command(name='add')
    async def add_name(self, ctx, name=None, user_id=None):
        """
        !badcomms add name @
        """
        member = ctx.guild.get_member_named(user_id)
        if name is not None and user_id is not None:
            name = name.lower().capitalize()
            id_number = user_id[3:-1]
            parameter = True

            for i in self.comms.keys():
                name_id = i.split("/")
                if name == name_id[0]:
                    parameter = False
                elif id_number == name_id[1]:
                    parameter = False
                elif member is not None:
                    if str(member.id) == name_id[1]:
                        parameter = False

            if parameter is True and user_id[:3] == "<@!":
                name_id = f"{name}/{id_number}"
                self.comms[name_id] = []
                await ctx.send(f"{ctx.author.display_name} added: {name}")
                self.save(ctx.guild.id)
            elif parameter is True:
                name_id = f"{name}/{member.id}"
                self.comms[name_id] = []
                await ctx.send(f"{ctx.author.display_name} added: {name}")
                self.save(ctx.guild.id)
            else:
                await ctx.send("Error: User might already be added, could be name or @")

    @badcomms.command(name='remark')
    async def give_remark(self, ctx, name=None, *, remark=None):
        """
        !badcomms remark name remark
        """
        if remark is not None:
            is_name_and_name_id = self.is_name_in_dict(name)  # Returns True or False to [0], name_id to [1] and name to [3]
            if is_name_and_name_id[0] is True:
                self.comms[is_name_and_name_id[1]].append(remark)
                self.save(ctx.guild.id)
                remarks = self.count_remarks(is_name_and_name_id[1])
                await ctx.send(
                    f"{str(ctx.author.display_name)} gave {is_name_and_name_id[2]} an remark because '{remark}', and now has {remarks} remarks.")
                return

    @badcomms.command(name='show')
    async def show_remarks(self, ctx, name=None):
        """
        !badcomms show name
        """
        if name is not None:
            is_name_and_name_id = self.is_name_in_dict(name)  # Returns True or False to [0], name_id to [1] and name to [3]
            if is_name_and_name_id[0] is True:
                my_embed = discord.Embed(
                    title=f"{str(ctx.author.display_name)} requested badcomms from: {is_name_and_name_id[2]}",
                    color=0x00ff00)
                x = 0
                for remark in self.comms[is_name_and_name_id[1]]:
                    my_embed.add_field(name=f"Badcomms nr: {x}", value=remark, inline=False)
                    x = x + 1
                await ctx.send(embed=my_embed)
                return

    @badcomms.command(name='leaderboard')
    async def leaderboard(self, ctx):
        """
        !badcomms leaderboard
        """
        my_embed = discord.Embed(title=f"{str(ctx.author.display_name)} requested badcommers leaderboard",
                                 color=0x00ff00)
        x = 0
        z = {}
        displayed = {}
        for person in self.comms:
            z[person] = self.count_remarks(person)

        order = sorted(z.values())

        for i in order[::-1]:
            for a, y in z.items():
                if i == y:
                    if a not in displayed.keys():
                        displayed[a] = y
                        my_embed.add_field(name=f"{x} {a.split('/')[0]}", value=f"Number of badcomms: {y}", inline=False)
                        x = x + 1
        await ctx.send(embed=my_embed)
    """
    @badcomms.command(name='help')
    async def help(self, ctx):
        await ctx.send('Help me')
    """
    @badcomms.group(name='vote')
    async def vote(self, ctx):
        """
        Add so they can see when next vote is
        """
        if ctx.invoked_subcommand is None:
            for guild_id, content in self.vote_servers.items():
                if str(guild_id) == str(ctx.guild.id):
                    await ctx.send(f"The next vote is {content[1][-2:]}-{content[1][5:7]}")
                    return

    @vote.command(name='add')
    async def vote_add(self, ctx, day=None, hours=None, role1=None, role2=None, role3=None):
        """
        !badcomms vote add date hours role role role
        """
        parameter = True
        for guild_id in self.vote_servers.keys():
            if str(ctx.guild.id) == str(guild_id):
                parameter = False

        if role3 is not None:
            if parameter is True:
                try:

                    day = int(day)
                    hours = int(hours)
                    self.vote_servers[ctx.guild.id] = [ctx.channel.id, self.new_date(day), False, hours, hours,
                                                       int(role1[3:-1]), int(role2[3:-1]),
                                                       int(role3[3:-1])]
                    self.save_servers()
                    await ctx.send("This server is now registered")
                except:
                    await ctx.send("Type '!badcomms help' for more info")
            else:
                await ctx.send("This server is already registered")
        else:
            await ctx.send("Type '!badcomms help' for more info")

    @vote.command(name='del')
    async def vote_del(self, ctx):
        """
        !badcomms del
        """
        parameter = False
        for guild_id in self.vote_servers.keys():
            if str(ctx.guild.id) == str(guild_id):
                parameter = True
        if parameter is True:
            if len(self.vote_servers) > 1:
                self.vote_servers.pop(ctx.guild.id)
            else:
                self.vote_servers = {}
            self.save_servers()

            await ctx.send("This server is now removed from the monthly vote.")

    @badcomms.command(name='test')
    async def test(self, ctx):
        await ctx.send(self.vote_servers)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        global voteList, vote0, vote1, vote2, vote3, vote4, vote5, vote6, vote7, vote8, vote9, votes, actualMessage
        try:
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
        except:
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
        for role in [r for r in self.bot.get_guild(int(x)).roles if r.id in role_ids]:
            for user in self.bot.get_guild(int(x)).members:
                if role in user.roles:
                    await user.remove_roles(role)
        for role in [r for r in self.bot.get_guild(int(x)).roles if r.id == role_ids[place-1]]:
            try:
                await channel.send(f"{name_id.split('/')[0]} has been placed {place} with votes({votes[number_votes]}) and badcomms({number_of_badcomms}), and is therefore granted the role '{role}' for bad comms")
                await self.bot.get_guild(int(x)).get_member(int(name_id.split("/")[1])).add_roles(role)
            except:
                return

    async def leaderboard_vote(self, x, y):
        global voteable
        self.load_comms(x)
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
                    self.remove_remarks(x)

    @show_time.before_loop
    async def before_show_time(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Badcomms(bot))
