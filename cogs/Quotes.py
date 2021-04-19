import random
import json
import discord
from discord.ext import commands

with open("cogs/Quotes_data/quote.json", encoding='utf-8') as f:
    quotes = json.load(f)

names = []
for i in quotes.keys():
    names.append(i)


class Quotes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='quote', help="Type '!quote help'")
    async def quote(self, ctx, *, arg="None"):
        def save():
            with open("cogs/Quotes_data/quote.json", "w", encoding='utf-8') as f:
                json.dump(quotes, f)

        if arg == "None":  # If the argument is the basic "None", it goes straight to random quote
            name = random.choice(names)

            if quotes[name] == []:
                response = f"Error no quote for: {name}"

            else:
                response = f"Quote from: {name} '{random.choice(quotes[name])}'"

            await ctx.send(response)

        elif arg.lower().capitalize() in names:  # Checks if the text is a name, if it is it sends a random quote from that name
            response = f"Quote from: {arg.lower().capitalize()} '{random.choice(quotes[arg.capitalize()])}'"

            await ctx.send(response)

        else:
            text_list = arg.split(" ")
            text = ""

            if text_list[0].lower() == "add":  # Runs if the add command is used
                if text_list[1].lower().capitalize() in names:
                    for i in text_list[2:]:
                        text = text + " " + i

                    quotes[text_list[1].lower().capitalize()].append(text)
                    await ctx.send(f"Quote from: {text_list[1].lower().capitalize()} '{text}' added")
                    save()

            elif text_list[0].lower() == "all":  # Runs if the all command is used
                if text_list[1].lower().capitalize() in names:
                    title_thing = f"All quotes from: {text_list[1].lower().capitalize()}"
                    myEmbed = discord.Embed(title=title_thing, color=0x00ff00)
                    x = 0

                    for i in quotes[text_list[1].lower().capitalize()]:
                        myEmbed.add_field(name=x, value=i, inline=False)
                        x = x + 1

                    await ctx.send(embed=myEmbed)

            elif text_list[0].lower() == "del":  # Runs if the delete command is used
                if text_list[1].lower().capitalize() in names:
                    index = int(text_list[2])
                    await ctx.send(
                        f"Removing quote from: {text_list[1].lower().capitalize()} '{quotes[text_list[1].lower().capitalize()].pop(index)}'")
                    save()

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
