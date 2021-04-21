import os.path
import random
import json
import discord
from discord.ext import commands
from pathlib import Path


class Quotes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.quotes = None
        self.names = []
        self.quotes_data_path = Path("cogs/Quotes_data/quote.json")
        self.load_quotes()

    def load_quotes(self):
        if os.path.isfile(self.quotes_data_path):
            with open(self.quotes_data_path, encoding='utf-8') as f:
                self.quotes = json.load(f)
        else:
            self.quotes = {"delete": ["me"]}
            with open(self.quotes_data_path, "x", encoding='utf-8') as f:
                json.dump(self.quotes, f)

        self.names = []
        for i in self.quotes.keys():
            self.names.append(i)

    def save(self):
        with open(self.quotes_data_path, "w", encoding='utf-8') as f:
            json.dump(self.quotes, f)

        self.names = []
        for i in self.quotes.keys():
            self.names.append(i)

    @commands.command(name='quote', help="Type '!quote help'")
    async def quote(self, ctx, *, arg="None"):

        if arg == "None":  # If the argument is the basic "None", it goes straight to random quote
            if self.names != []:
                name = random.choice(self.names)

                if self.quotes[name] == []:
                    response = f"Error no quote for: {name}"

                else:
                    response = f"{str(ctx.author)[:-5]} random quote from: {name} '{random.choice(self.quotes[name])}'"

                await ctx.send(response)
            else:
                await ctx.send("No users detected, please add one. '!quote help' for more help.")

        elif arg.lower().capitalize() in self.names:  # Checks if the text is a name, if it is it sends a random quote from that name
            if self.quotes[arg.lower().capitalize()] == []:
                response = f"Error no quote for: {arg.lower().capitalize()}"
            else:
                response = f"{str(ctx.author)[:-5]} requested quote from: {arg.lower().capitalize()} '{random.choice(self.quotes[arg.capitalize()])}'"

            await ctx.send(response)

        else:
            text_list = arg.split(" ")
            text = ""
            command = text_list[0].lower()


            if command.capitalize() in self.names:
                for i in text_list[1:]:
                    text = text + " " + i

                self.quotes[command.capitalize()].append(text)
                await ctx.send(f"{str(ctx.author)[:-5]} added quote from: {command.capitalize()} '{text}' added")
                self.save()

            elif command == "all":  # Runs if the all command is used
                if len(text_list) == 2:
                    lname = text_list[1].lower().capitalize()
                    if lname in self.names:
                        title_thing = f"{str(ctx.author)[:-5]} requested all quotes from: {lname}"
                        myEmbed = discord.Embed(title=title_thing, color=0x00ff00)
                        x = 0

                        for i in self.quotes[lname]:
                            myEmbed.add_field(name=x, value=i, inline=False)
                            x = x + 1

                        await ctx.send(embed=myEmbed)

            elif command == "del":  # Runs if the delete command is used
                if len(text_list) == 3:
                    lname = text_list[1].lower().capitalize()
                    if lname in self.names:
                        index = int(text_list[2])
                        if self.quotes[lname] != [] and len(self.quotes[lname])-1 >= index:
                            await ctx.send(
                                f"{str(ctx.author)[:-5]} removing quote from: {lname} '{self.quotes[lname].pop(index)}'")
                            self.save()
                        else:
                            await ctx.send("That quote does not exist")

            elif command == "add":
                if len(text_list) == 2:
                    lname = text_list[1].lower().capitalize()
                    if lname not in self.names:
                        self.quotes[lname] = []
                        await ctx.send(f"{str(ctx.author)[:-5]} added: {lname}")
                        self.save()

            elif command == "delete":
                if len(text_list) == 2:
                    lname = text_list[1].lower().capitalize()
                    if lname in self.names:
                        await ctx.send(f"{str(ctx.author)[:-5]} deleted: {lname}")
                        self.quotes.pop(lname)
                        self.save()

            elif command == "help":  # Runs if the help command is used
                if len(text_list) == 1:
                    myEmbed = discord.Embed(title=f"Helping {str(ctx.author)[:-5]}", color=0x00ff00)
                    myEmbed.add_field(name="See quotes",
                                      value="To see random quotes type '!quote' or '!quote person' to get personalized quotes",
                                      inline=False)
                    myEmbed.add_field(name="Add quotes", value="To add quotes type '!quote person quote'", inline=False)
                    myEmbed.add_field(name="All quotes", value="To see all quotes from person type '!quote all person'",
                                      inline=False)
                    myEmbed.add_field(name="Delete quotes",
                                      value="To delete quotes type '!quote del person number'(The number is correlating to the all list)",
                                      inline=False)
                    myEmbed.add_field(name="Add person", value="To add quotes type '!quote add person'", inline=False)
                    myEmbed.add_field(name="Delete person", value="To add quotes type '!quote delete person'", inline=False)
                    await ctx.send(embed=myEmbed)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Quotes(bot))
