from discord.ext import commands
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import discord
from urllib.parse import urljoin
"""
Show daily matches with info,
    en stor spesiell disc melding,
Show expanded info on some matches
Track certain teams and get to know everytime they play
"""


class HLTVScraper(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.matches = None

    def download_matches(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        req = Request("https://www.hltv.org/matches", headers=headers)
        html = urlopen(req, timeout=10)
        self.matches = BeautifulSoup(html.read(), 'html.parser')

    @commands.command()
    async def match(self, ctx):
        self.download_matches()
        allMatches = self.matches.find('div', {'class':'upcomingMatchesSection'})
        date = allMatches.span.text.replace(" ", "").split("-")

        embed = discord.Embed(title=f"Matches {date[0]}, {date[3]}-{date[2]}-{date[1]}", url="https://www.hltv.org/matches",
                              description=f"A list of CSGO matches", color=0xff0000)
        for name1, name2 in zip(allMatches.find_all('div', {'class':'matchTeam team1'}), allMatches.find_all('div', {'class':'matchTeam team2'})):

            matchInfo = name1.parent.parent.find('div', {'class':'matchInfo'})
            urlHalf = name1.parent.parent.get('href')
            eventName = name1.parent.parent.find('div', {'class':'matchEventName'}).text
            time = matchInfo.find('div', {'class':'matchTime'}).text
            stars = len(matchInfo.find_all('i', {'class':'fa fa-star'}))
            matchMeta = matchInfo.find('div', {'class':'matchMeta'}).text
            url = urljoin('https://www.hltv.org/matches', urlHalf)

            name1 = name1.find('div', {'class':'matchTeamLogoContainer'})
            name2 = name2.find('div', {'class': 'matchTeamLogoContainer'})
            embed.add_field(name=f"{time}  {name1.img.get('title')} VS {name2.img.get('title')}. {':star:'*stars}",
                            value=f"Format: {matchMeta}.\nTournament: {eventName}\n"
                                  f"[HLTV page]({url})", inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(HLTVScraper(bot))
