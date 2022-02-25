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
Add Tournament url
Results and Live
"""


class HLTVScraper(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.matches = None
        self.matchInfo = {
            'day1info': {
                'date': "",  # date
                'team1': [],  # name1
                'team2': [],  # name2
                'stars': [],  # Stars
                'matchMeta': [],  # matchMeta
                'time': [],  # time
                'url': [],  # url
                'eventName': []  # eventName
            },
            'day2info': {
                'date': "",  # date
                'team1': [],  # name1
                'team2': [],  # name2
                'matchMeta': [],  # matchMeta
                'time': [],  # time
                'url': [],  # url
                'eventName': []  # eventName
            }
        }
        self.liveMatches = {
        'team1': [],  # name1
        'team2': [],  # name2
        'stars': [],  # Stars
        'matchMeta': [],  # matchMeta
        'time': [],  # time its live, I dont need
        'url': [],  # url
        'eventName': [],  # eventName
        'score1' : "",  # Score is not gonna work atm
        'maps1' : "",  # Map score is not gonna work atm
        'score2' : "",  # Score is not gonna work atm
        'maps2': ""  # Map score is not gonna work atm
        }
        self.html1 = None

    def download_matches(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        req = Request("https://www.hltv.org/matches", headers=headers)
        html = urlopen(req, timeout=10)

        self.matches = BeautifulSoup(html.read(), 'html.parser')
        self.matches_dict()

    def matches_dict(self):

        self.matchInfo = {
            'day1info': {
                'date': "",  # date
                'team1' : [],  # name1
                'team2' : [],  # name2
                'stars' : [],  # Stars
                'matchMeta' : [],  # matchMeta
                'time' : [],  # time
                'url' : [],  # url
                'eventName' : []  # eventName
            },
            'day2info': {
                'date': "",  # date
                'team1': [],  # name1
                'team2': [],  # name2
                'stars': [],  # Stars
                'matchMeta': [],  # matchMeta
                'time': [],  # time
                'url': [],  # url
                'eventName': []  # eventName
            }
        }

        allMatchesUpcoming = self.matches.find_all('div', {'class': 'upcomingMatchesSection'})
        allMatchesDay1 = allMatchesUpcoming[0]
        allMatchesDay2 = allMatchesUpcoming[1]
        self.matchInfo['day1info']["date"] = allMatchesDay1.span.text.replace(" ", "").split("-")
        self.matchInfo['day2info']["date"] = allMatchesDay2.span.text.replace(" ", "").split("-")

        for team1, team2 in zip(allMatchesDay1.find_all('div', {'class': 'matchTeam team1'}),
                                allMatchesDay1.find_all('div', {'class': 'matchTeam team2'})):

            matchInfo = team1.parent.parent.find('div', {'class': 'matchInfo'})
            eventName = team1.parent.parent.find('div', {'class': 'matchEventName'}).text
            self.matchInfo['day1info']["eventName"].append(eventName)
            time = matchInfo.find('div', {'class': 'matchTime'}).text
            self.matchInfo['day1info']["time"].append(time)
            stars = len(matchInfo.find_all('i', {'class': 'fa fa-star'}))
            self.matchInfo['day1info']["stars"].append(stars)
            matchMeta = matchInfo.find('div', {'class': 'matchMeta'}).text
            self.matchInfo['day1info']["matchMeta"].append(matchMeta)
            url = urljoin('https://www.hltv.org/matches', team1.parent.parent.get('href'))
            self.matchInfo['day1info']["url"].append(url)

            name1 = team1.find('div', {'class':'text-ellipsis'}).text
            name2 = team2.find('div', {'class':'text-ellipsis'}).text
            self.matchInfo['day1info']["team1"].append(name1)
            self.matchInfo['day1info']["team2"].append(name2)

        for team1, team2 in zip(allMatchesDay2.find_all('div', {'class': 'matchTeam team1'}),
                                allMatchesDay2.find_all('div', {'class': 'matchTeam team2'})):

            matchInfo = team1.parent.parent.find('div', {'class': 'matchInfo'})
            eventName = team1.parent.parent.find('div', {'class': 'matchEventName'}).text
            self.matchInfo['day2info']["eventName"].append(eventName)
            time = matchInfo.find('div', {'class': 'matchTime'}).text
            self.matchInfo['day2info']["time"].append(time)
            stars = len(matchInfo.find_all('i', {'class': 'fa fa-star'}))
            self.matchInfo['day2info']["stars"].append(stars)
            matchMeta = matchInfo.find('div', {'class': 'matchMeta'}).text
            self.matchInfo['day2info']["matchMeta"].append(matchMeta)
            url = urljoin('https://www.hltv.org/matches', team1.parent.parent.get('href'))
            self.matchInfo['day2info']["url"].append(url)

            name1 = team1.find('div', {'class':'text-ellipsis'}).text
            name2 = team2.find('div', {'class':'text-ellipsis'}).text
            self.matchInfo['day2info']["team1"].append(name1)
            self.matchInfo['day2info']["team2"].append(name2)

    def live_match_dict(self):
        live = self.matches.find('div', {'class':'liveMatchesContainer'})
        self.liveMatches = {
        'team1': [],  # name1
        'team2': [],  # name2
        'stars': [],  # Stars
        'matchMeta': [],  # matchMeta
        'time': [],  # time its live, I dont need
        'url': [],  # url
        'eventName': [],  # eventName
        'score1' : "",  # Score is not gonna work atm
        'maps1' : "",  # Map score is not gonna work atm
        'score2' : "",  # Score is not gonna work atm
        'maps2': ""  # Map score is not gonna work atm
        }
        if live is not None:
            liveMatches = live.find_all('div', {'class':'liveMatch'})

            for liveMatch in liveMatches:
                self.liveMatches['team1'].append(liveMatch.find('div', {'class':'matchTeams'}).find_all('div', {'class':'matchTeamName'})[0].text)
                self.liveMatches['eventName'].append(liveMatch.find('div', {'class': 'matchEventName'}).text)
                self.liveMatches['stars'].append(len(liveMatch.find_all('i', {'class': 'fa fa-star'})))
                self.liveMatches['matchMeta'].append(liveMatch.find('div', {'class': 'matchMeta'}).text)
                self.liveMatches['url'].append(urljoin('https://www.hltv.org/matches', liveMatch.find('a', {'class': 'match a-reset'}).get("href")))
                self.liveMatches['team2'].append(liveMatch.find('div', {'class':'matchTeams'}).find_all('div', {'class':'matchTeamName'})[1].text)




    @commands.command(name="show")
    async def show_today_matches(self, ctx, stars=None):
        await ctx.send(embed=self.make_embed_future_matches("day1info", stars))

    @commands.command(name="showTm")
    async def show_tomorrow_matches(self, ctx, stars=None):
        await ctx.send(embed=self.make_embed_future_matches("day2info", stars))

    @commands.command(name="showLive")
    async def show_live_matches(self, ctx, stars=None):
        await ctx.send(embed=self.make_embed_live_matches(stars))

    def make_embed_future_matches(self, day, star=None):
        #if self.matchInfo[day]['team1'] == []:
        self.download_matches()

        embed = discord.Embed(
            title=f"Matches {self.matchInfo[day]['date'][0]}, {self.matchInfo[day]['date'][3]}-{self.matchInfo[day]['date'][2]}-{self.matchInfo[day]['date'][1]}",
            url="https://www.hltv.org/matches",
            description=f"A list of CSGO matches", color=0xff0000)

        for i in range(len(self.matchInfo[day]['team1'])):
            if star is not None:
                if int(star) > self.matchInfo[day]['stars'][i]:
                    continue

            embed.add_field(
                name=f"{self.matchInfo[day]['time'][i]}  {self.matchInfo[day]['team1'][i]} VS {self.matchInfo[day]['team2'][i]}. {':star:' * self.matchInfo[day]['stars'][i]}",
                value=f"Format: {self.matchInfo[day]['matchMeta'][i]}.\nTournament: {self.matchInfo[day]['eventName'][i]}\n"
                      f"[HLTV page]({self.matchInfo[day]['url'][i]})", inline=False)
        return embed

    def make_embed_live_matches(self, star=None): # Add så star gjer nokke
        #if self.liveMatches['team1'] == []:  # Trengst denna?
        self.download_matches()
        self.live_match_dict()

        embed = discord.Embed(
            title=f":red_circle: Live matches",
            url="https://www.hltv.org/matches",
            description=f"A list of live CSGO matches", color=0xff0000)

        for i in range(len(self.liveMatches['team1'])):
            if star is not None:
                if int(star) > self.liveMatches['stars'][i]:
                    continue
            embed.add_field(
                name=f":red_circle: Live  {self.liveMatches['team1'][i]} VS {self.liveMatches['team2'][i]}. {':star:' * self.liveMatches['stars'][i]}",
                value=f"Format: {self.liveMatches['matchMeta'][i]}.\nTournament: {self.liveMatches['eventName'][i]}\n"
                      f"[HLTV page]({self.liveMatches['url'][i]})", inline=False)

        return embed

def setup(bot):
    bot.add_cog(HLTVScraper(bot))
