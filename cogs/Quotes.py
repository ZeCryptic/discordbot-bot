import os.path
import random
import json
import discord
from discord.ext import commands
from pathlib import Path

"""
TO DO
General cleanup
Add so if there is no quote from user, user doesnt get picked for random quote
Make it so the add can add a new person with or without quote or add a quote to existing person
"""


class Quotes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.names = []
        self.quotes = None
        self.quotes_data_path = Path("cogs/Quotes_data")

    def load_quotes(self, guild_id):
        path = self.quotes_data_path / f"{guild_id}_quotes.json"

        if not os.path.exists(self.quotes_data_path):
            os.makedirs(self.quotes_data_path)
        if os.path.isfile(path):
            with open(path, encoding='utf-8') as f:
                self.quotes = json.load(f)

        else:
            self.quotes = {}
            with open(path, "x", encoding='utf-8') as f:
                json.dump(self.quotes, f)

        self.names = []
        for i in self.quotes.keys():
            self.names.append(i)

    def save_quotes(self, guild_id):
        path = self.quotes_data_path / f"{guild_id}_quotes.json"

        if not os.path.exists(self.quotes_data_path):
            os.makedirs(self.quotes_data_path)
        with open(path, "w", encoding='utf-8') as f:
            json.dump(self.quotes, f, indent=6)

        self.names = []
        for i in self.quotes.keys():
            self.names.append(i)

    @commands.group(name="quote")
    async def quote(self, ctx):
        self.load_quotes(ctx.guild.id)
        if ctx.invoked_subcommand is None:
            if len(self.quotes) >= 1:
                await self.random_quote(ctx)
            else:
                await ctx.send("There is no one to quote")

    @quote.command(name="add")
    async def add_quote_and_person(self, ctx, name=None, *, quote=None):
        if name is not None:
            name = name.lower().capitalize()
            if quote is not None:
                if name in self.names:
                    self.quotes[name].append(quote)
                    await ctx.send(f'{str(ctx.author.display_name)} added quote from: {name} "{quote}" added')
                else:
                    self.quotes[name] = [quote]
                    await ctx.send(f'{str(ctx.author.display_name)} added person and quote from: {name} "{quote}" added')
            else:
                if name not in self.names:
                    self.quotes[name] = []
                    await ctx.send(f"{str(ctx.author.display_name)} added: {name}")
                else:
                    await ctx.send(f'{name} already added')
        self.save_quotes(ctx.guild.id)

    @quote.command(name="from")
    async def from_name(self, ctx, name=None):
        if name is not None:
            name = name.lower().capitalize()
            if name in self.names:
                if self.quotes[name] == []:
                    await ctx.send(f"Error no quote for: {name}")
                else:
                    await ctx.send(f'{str(ctx.author.display_name)} requested quote from: {name} "{random.choice(self.quotes[name])}"')

    @quote.command(name="all")
    async def show_all_quotes_from(self, ctx, name=None):
        if name is not None:
            name = name.lower().capitalize()
            if name in self.names:
                title_thing = f"{str(ctx.author.display_name)} requested all quotes from: {name}"
                my_embed = discord.Embed(title=title_thing, color=0x00ff00)
                x = 0

                for i in self.quotes[name]:
                    my_embed.add_field(name=x, value=i, inline=False)
                    x = x + 1

                await ctx.send(embed=my_embed)

    @quote.command(name="del")
    async def delete_quote(self, ctx, name=None, index=None):
        if name is not None:
            name = name.lower().capitalize()
            if index is not None and name in self.names:
                try:
                    index = int(index)
                except:
                    return
                if self.quotes[name] != [] and len(self.quotes[name]) - 1 >= index:
                    await ctx.send(
                        f'{str(ctx.author.display_name)} removing quote from: {name} "{self.quotes[name].pop(index)}"')
                    self.save_quotes(ctx.guild.id)

    @quote.command(name="delete")
    async def delete_name(self, ctx, name=None):
        if name is not None:
            name = name.lower().capitalize()
            if name in self.names:
                await ctx.send(f"{str(ctx.author.display_name)} deleted: {name}")
                self.quotes.pop(name)
                self.save_quotes(ctx.guild.id)

    @quote.command(name="everyone")
    async def list_all_quoters(self, ctx):
        my_embed = discord.Embed(title="See everyone, and how many quotes they have", color=0x00ff00)
        for name, quotes in self.quotes.items():
            my_embed.add_field(name=name, value=f"And has {len(quotes)} quote(s)", inline=False)
        await ctx.send(embed=my_embed)

    @quote.command(name="help")
    async def help(self, ctx):
        my_embed = discord.Embed(title=f"Helping {str(ctx.author.display_name)}", color=0x00ff00)
        my_embed.add_field(name="READ ME", value="[] is not a part of the commands, it is only used to show where you input names etc.")
        my_embed.add_field(name="See quotes",
                          value='To see random quotes type "!quote" or "!quote from [person]" to get personalized quotes',
                          inline=False)
        my_embed.add_field(name="Add quotes", value='To add quotes type "!quote add [person] [quote]"', inline=False)
        my_embed.add_field(name="All quotes", value='To see all quotes from person type "!quote all [person]"',
                          inline=False)
        my_embed.add_field(name="Delete quotes",
                          value="To delete quotes type '!quote del person number'(The number is correlating to the all list)",
                          inline=False)
        my_embed.add_field(name="Add person", value='To add person type "!quote add [person]", you can also add quotes from them with adding the quote behind', inline=False)
        my_embed.add_field(name="Delete person", value='To delete person type "!quote delete [person]"', inline=False)
        my_embed.add_field(name="See all who can be quoted", value='To see all who can be quoted type "!quote everyone"')
        await ctx.send(embed=my_embed)

    @quote.command(name="transfer")
    async def transfer_old_quotes(self, ctx):
        if os.path.isfile(Path("cogs/Quotes_data/quote.json")):
            with open(Path("cogs/Quotes_data/quote.json"), encoding='utf-8') as f:
                self.quotes = json.load(f)
        else:
            self.quotes = {}
            with open(Path("cogs/Quotes_data/quote.json"), "x", encoding='utf-8') as f:
                json.dump(self.quotes, f)

        new_quotes = {}
        for x in self.quotes.keys():
            new_quotes[x] = []
            for i in self.quotes[x]:
                new_quotes[x].append(i[1:])

        path = self.quotes_data_path / f"{ctx.guild.id}_quotes.json"

        if not os.path.exists(self.quotes_data_path):
            os.makedirs(self.quotes_data_path)
        with open(path, "w", encoding='utf-8') as f:
            json.dump(new_quotes, f, indent=6)

    async def random_quote(self, ctx, number_of_tries=0):
        if number_of_tries < 9:
            name = random.choice(self.names)
            if self.quotes[name] == []:
                await self.random_quote(ctx, number_of_tries+1)
            else:
                await ctx.send(f'{str(ctx.author.display_name)} random quote from: {name} "{random.choice(self.quotes[name])}"')
        else:
            await ctx.send("No quotes was found")


def setup(bot):
    bot.add_cog(Quotes(bot))
