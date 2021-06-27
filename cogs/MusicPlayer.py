from discord.ext import commands
from discord import FFmpegPCMAudio
from shutil import which
import typing
import discord
import datetime
import youtube_dl as yt

yt_format_info = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}


def user_is_connected(ctx):
    return ctx.author.voice.channel is not None


class MusicPlayer(commands.Cog):

    def __init__(self, bot):
        self.queue = []
        self.bot = bot
        self.voice_connection = None
        self.currently_playing_info = None

    def voice_connected(self):
        return self.voice_connection is not None

    def get_yt_video_info(self, search):
        with yt.YoutubeDL(yt_format_info) as yt_dl:
            info = yt_dl.extract_info(f'ytsearch:{search}', download=False)['entries'][0]
            return info

    def play_audio(self, video_info):
        audio_url = video_info['url']
        self.currently_playing_info = video_info
        self.voice_connection.play(FFmpegPCMAudio(audio_url), after=self.play_next_in_queue)

    def play_next_in_queue(self, error):
        if not self.queue:
            return

        video_info = self.queue.pop(0)
        self.play_audio(video_info)

    @commands.command(help="Searches youtube for a video and plays the audio source or adds it to the queue"
                           ". Usage: !play [search/link]")
    @commands.check(user_is_connected)
    async def play(self, ctx, *user_input):
        user_input = ' '.join(user_input)
        if not self.voice_connected():
            await self.join(ctx)

        await ctx.send(f'Searching for: `{user_input}`')
        video_info = self.get_yt_video_info(user_input)
        video_title = video_info['title']

        if self.voice_connection.is_playing() or self.voice_connection.is_paused():
            self.queue.append(video_info)
            await ctx.send(f'Added `{video_title}` to position **{len(self.queue)}** in queue')

        else:
            self.play_audio(video_info)
            await ctx.send(f'Now playing: `{video_title}`')

    @commands.command(help="Makes the bot join the voice channel of the caller")
    async def join(self, ctx):
        self.voice_connection = await ctx.author.voice.channel.connect()
        await ctx.send(f'Joined voice channel: `{ctx.author.voice.channel.name}`')

    @commands.command(help="Pauses audio playback")
    async def pause(self, ctx):
        self.voice_connection.pause()
        await ctx.send('⏸ Pausing music')

    @commands.command(help="Resumes audio playback")
    async def resume(self, ctx):
        self.voice_connection.resume()
        await ctx.send('▶️ Resuming music')

    @commands.command(help="Stops audio playback and clears the queue")
    async def stop(self, ctx):
        self.queue = []
        self.currently_playing_info = None
        self.voice_connection.stop()
        if ctx: await ctx.send('⏹️ Stopping music and clearing queue')

    @commands.command()
    async def seek(self, ctx):
        pass

    @commands.command(help="Skips to the next in queue")
    async def skip(self, ctx):
        self.voice_connection.stop()
        await ctx.send('⏭️ Skipping to next in queue')

    @commands.command()
    async def np(self, ctx):
        pass

    @commands.command(help="Shows the audio queue. Usage: !queue [page number](optional)")
    async def queue(self, ctx, page: typing.Optional[int] = 1):
        pages = (len(self.queue) // 10) + 1
        if page > pages:
            page = pages
        elif page < 1:
            page = 1

        embed = discord.Embed(title='Music player queue')
        embed.description = f'**{len(self.queue)}** in queue.\n Currently playing: `{self.currently_playing_info["title"]}`'
        for i in range(10):
            i += (page - 1)*10
            if i > len(self.queue) - 1:
                break
            info = self.queue[i]
            field_name = f'{i + 1}: `{info["title"]}`'
            field_value = f' {datetime.timedelta(seconds=info["duration"])} | ' \
                          f'👍 {info["like_count"]} 👎 {info["dislike_count"]} | ' \
                          f'📈 {info["view_count"]}'
            embed.add_field(name=field_name, value=field_value, inline=False)
        embed.set_footer(text=f'Page {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command()
    async def clear(self, ctx):
        pass

    @commands.command(help="Leaves the connected voice channel and clears the queue")
    async def leave(self, ctx):
        await self.stop(None)
        await self.voice_connection.disconnect()
        await ctx.send('Leaving voice channel')
        self.voice_connection = None

    def cog_unload(self):
        # TODO: Find a way to disconnect bot when cog is unloaded without it being a coroutine
        # (rare bug causes the bot to keep playing even after the cog is not available)
        pass


def setup(bot):
    if which('ffmpeg') is None:
        raise FileNotFoundError('ffmpeg was not found or is not installed')
    bot.add_cog(MusicPlayer(bot))
