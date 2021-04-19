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
            self.quotes = {"Nei": ["hei"]}
            with open(self.quotes_data_path, "x", encoding='utf-8') as f:
                json.dump(self.quotes, f)

        for i in self.quotes.keys():
            self.names.append(i)

    def save(self):
        with open(self.quotes_data_path, "w", encoding='utf-8') as f:
            json.dump(self.quotes, f)

    @commands.command(name='quote', help="Type '!quote help'")
    async def quote(self, ctx, *, arg="None"):

        if arg == "None":  # If the argument is the basic "None", it goes straight to random quote
            name = random.choice(self.names)

            if self.quotes[name] == []:
                response = f"Error no quote for: {name}"

            else:
                response = f"Quote from: {name} '{random.choice(self.quotes[name])}'"

            await ctx.send(response)

        elif arg.lower().capitalize() in self.names:  # Checks if the text is a name, if it is it sends a random quote from that name
            response = f"Quote from: {arg.lower().capitalize()} '{random.choice(self.quotes[arg.capitalize()])}'"

            await ctx.send(response)

        else:
            text_list = arg.split(" ")
            text = ""

            if text_list[0].lower() == "add":  # Runs if the add command is used
                if text_list[1].lower().capitalize() in self.names:
                    for i in text_list[2:]:
                        text = text + " " + i

                    self.quotes[text_list[1].lower().capitalize()].append(text)
                    await ctx.send(f"Quote from: {text_list[1].lower().capitalize()} '{text}' added")
                    self.save()

            elif text_list[0].lower() == "all":  # Runs if the all command is used
                if text_list[1].lower().capitalize() in self.names:
                    title_thing = f"All quotes from: {text_list[1].lower().capitalize()}"
                    myEmbed = discord.Embed(title=title_thing, color=0x00ff00)
                    x = 0

                    for i in self.quotes[text_list[1].lower().capitalize()]:
                        myEmbed.add_field(name=x, value=i, inline=False)
                        x = x + 1

                    await ctx.send(embed=myEmbed)

            elif text_list[0].lower() == "del":  # Runs if the delete command is used
                if text_list[1].lower().capitalize() in self.names:
                    index = int(text_list[2])
                    await ctx.send(
                        f"Removing quote from: {text_list[1].lower().capitalize()} '{self.quotes[text_list[1].lower().capitalize()].pop(index)}'")
                    self.save()

            elif text_list[0].lower() == "help":  # Runs if the help command is used
                myEmbed = discord.Embed(title="Help", color=0x00ff00)
                myEmbed.add_field(name="See quotes",
                                  value="To see random quotes type '!quote' or '!quote person' to get personalized quotes",
                                  inline=False)
                myEmbed.add_field(name="Add quotes", value="To add quotes type '!quote add person quote'", inline=False)
                myEmbed.add_field(name="All quotes", value="To see all quotes from person type '!quote all person'",
                                  inline=False)
                myEmbed.add_field(name="Delete quotes",
                                  value="To delete quotes type '!quote del person number'(The number is correlating to the all list)",
                                  inline=False)
                await ctx.send(embed=myEmbed)
