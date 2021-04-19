import json
import discord
import os.path
from discord.ext import commands

if os.path.isfile("cogs/Badcomms_data/comms.json"):
    with open("cogs/Badcomms_data/comms.json", encoding='utf-8') as f:
        quotes = json.load(f)
else:
    comms = {
        "Victor": [],
        "Simen": [],
        "Leander": [],
        "Lade": [],
        "Alek": [],
        "Finni": [],
        "H\u00e5kon": [],
        "Sigurd": [],
        "Thomas": []}
    with open("cogs/Badcomms_data/comms.json", "x", encoding='utf-8') as f:
        json.dump(comms, f)

cNames = []
for i in comms.keys():
    cNames.append(i)

# noinspection PyGlobalUndefined
class Badcomms(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='badcomms', help="elp'")
    async def bad_comms(self, ctx, person=None, *, arg=None):
        def save():
            with open("cogs/Badcomms_data/comms.json", "w", encoding='utf-8') as f:
                json.dump(comms, f, indent=6)

        def count_remarks(person):
            x = 0
            for i in comms[person]:
                x = x + 1
            return x

        if person != None:
            if person.lower().capitalize() in cNames:
                comms[person.lower().capitalize()].append(arg)
                save()
                remarks = count_remarks(person.lower().capitalize())
                await ctx.send(f"{person.lower().capitalize()} now has {remarks} remarks")

            elif person.lower().capitalize() == "Vote":
                myEmbed = discord.Embed(title="Badcommers", color=0x00ff00)
                x = 0
                for person in comms:
                    z = count_remarks(person)
                    myEmbed.add_field(name=f"{x} {person}", value=f"Number of badcomms: {z}", inline=False)
                    x = x + 1
                message = await ctx.send(embed=myEmbed)
                emojis = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
                global voteList, vote0, vote1, vote2, vote3, vote4, vote5, vote6, vote7, vote8, votes, actualMessage
                actualMessage = message
                voteList = []
                votes = {"vote0": 0, "vote1": 0, "vote2": 0, "vote3": 0, "vote4": 0, "vote5": 0, "vote6": 0, "vote7": 0, "vote8": 0}
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
                    await ch.send(f"{cNames[index]} has the most votes({x}) for bad comms")