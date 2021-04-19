import json
import discord
from discord.ext import commands

with open("cogs/Badcomms_data/comms.json", encoding='utf-8') as f:
    comms = json.load(f)

cNames = []
for i in comms.keys():
    cNames.append(i)


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
                for emoji in emojis[:x]:
                    await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        user_list = []
        emoji = reaction.emoji
        print(user)
        if user.bot:
            return
        if user not in user_list:
            user_list.append(user)
            if emoji == "0️⃣":
                print("yeet")
            elif emoji == "1️⃣":
                print("yeet")
            elif emoji == "2️⃣":
                print("yeet")
            elif emoji == "3️⃣":
                print("yeet")
            elif emoji == "4️⃣":
                print("yeet")
            elif emoji == "5️⃣":
                print("yeet")
            elif emoji == "6️⃣":
                print("yeet")
            elif emoji == "7️⃣":
                print("yeet")
            elif emoji == "8️⃣":
                print("yeet")
            else:
                return
