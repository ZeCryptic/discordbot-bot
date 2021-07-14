from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument
from dotenv import load_dotenv
import os
import requests


class GoogleImages(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        load_dotenv()
        self.google_token = os.getenv('GOOGLE_TOKEN')
        self.google_engine_id = os.getenv('SEARCH_ENGINE_ID')
        if not self.google_token:
            raise Exception('GOOGLE_TOKEN not found in .env')
        elif not self.google_engine_id:
            raise Exception('SEARCH_ENGINE_ID not found in .env')

    @commands.command(help='Searches for an image and posts the first result', aliases=['g', 'img'])
    async def google(self, ctx, search: str):
        # TODO: implement error checking and handling (check for non-400 error messages)
        arguments = {'key': self.google_token, 'cx': self.google_engine_id, 'q': search,
                     'num': '1', 'searchType': 'image'}
        r = requests.get('https://www.googleapis.com/customsearch/v1?', params=arguments).json()
        try:
            response = r['items'][0]['link']
        except KeyError:
            response = 'No results for the search or the daily search limit was reached'
        await ctx.send(response)

    @google.error
    async def google_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send('Missing required argument')

def setup(bot):
    bot.add_cog(GoogleImages(bot))