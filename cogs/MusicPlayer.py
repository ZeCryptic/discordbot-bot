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


class UserNotInVoiceChannel(commands.CheckFailure):
    pass


class BotNotInVoiceChannel(commands.CheckFailure):
    pass


def user_is_in_voice(ctx):
    if ctx.author.voice is not None:
        return True
    else:
        raise UserNotInVoiceChannel('You need to be in a voice channel to use this command')


class MusicPlayer(commands.Cog):

    def __init__(self, bot):
        self.queue = []
        self.bot = bot
        self.voice_connection = None
        self.currently_playing_info = None
        self.start_time = None
        self.s_time_delta = datetime.timedelta(0)

    async def check_bot_voice_connected(self, ctx):
        # TODO: Find a way to make this into a check decorator
        if self.voice_connection is not None:
            return True
        else:
            await ctx.send('Bot needs to be in a voice channel to use this command')
            return False

    def get_yt_video_info(self, search):
        with yt.YoutubeDL(yt_format_info) as yt_dl:
            info = yt_dl.extract_info(f'ytsearch:{search}', download=False)['entries'][0]
            return info

    def play_audio(self, video_info):
        audio_url = video_info['url']
        self.currently_playing_info = video_info
        self.voice_connection.play(FFmpegPCMAudio(audio_url), after=self.play_next_in_queue)
        self._start_time()

    def play_next_in_queue(self, error):
        if not self.queue:
            self.currently_playing_info = None
            return

        video_info = self.queue.pop(0)
        self.play_audio(video_info)

    def _get_video_information_embed(self, info, time_stamp=None):
        duration = datetime.timedelta(seconds=info["duration"])
        embed = discord.Embed(title=info['title'], url=f'https://www.youtube.com/watch?v={info["id"]}')
        embed.set_image(url=f'http://img.youtube.com/vi/{info["id"]}/mqdefault.jpg')
        embed.set_footer(text=f'{duration} | ' \
                              f'👍 {info["like_count"]} 👎 {info["dislike_count"]} | ' \
                              f'📈 {info["view_count"]}')
        if not time_stamp:
            return embed

        progress_bar = ['▬']*20
        time_placement = int((time_stamp.seconds / int(info["duration"])) * len(progress_bar))
        progress_bar.insert(time_placement, '🔘')
        field_name = '🎵 Now playing: 🎵' if self.voice_connection.is_playing() else '⏸️ Music Paused'
        embed.add_field(name=field_name, value=f"`{''.join(progress_bar)}`\n"
                                                         f"{str(time_stamp).split('.')[0]} / {duration}")
        return embed

    def _start_time(self):
        self.start_time = datetime.datetime.now()
        self.s_time_delta = datetime.timedelta(0)

    def _pause_time(self):
        self.s_time_delta += datetime.datetime.now() - self.start_time

    def _resume_time(self):
        self.start_time = datetime.datetime.now()

    def _get_time(self):
        if self.voice_connection.is_paused():
            return self.s_time_delta
        else:
            return self.s_time_delta + (datetime.datetime.now() - self.start_time)

    @commands.group(help="Music commands which lets the user play audio from youtube sources in a voice channel")
    @commands.check(user_is_in_voice)
    async def music(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Type '<prefix>music play [search]/[link]' to play music in your voice channel or"
                           "'<prefix>help music' for list of music related commands")

    @music.command(help="Searches youtube for a video and plays the audio source or adds it to the queue"
                        ". Usage: !play [search/link]")
    async def play(self, ctx, *user_input):
        if not user_input:
            await ctx.send('You need to provide a search term or a link to a youtube video')
            return

        user_input = ' '.join(user_input)
        if self.voice_connection is None:
            await self.join(ctx)

        video_info = self.get_yt_video_info(user_input)
        video_title = video_info['title']
        await ctx.send(f'Searched for `{user_input}` and found:', embed=self._get_video_information_embed(video_info))

        if self.voice_connection.is_playing() or self.voice_connection.is_paused():
            self.queue.append(video_info)
            await ctx.send(f'Added `{video_title}` to position **{len(self.queue)}** in queue')

        else:
            self.play_audio(video_info)
            await ctx.send(f'Now playing: `{video_title}`')

    @music.command(help="Makes the bot join the voice channel of the caller")
    async def join(self, ctx):
        if self.voice_connection is not None:
            await self.leave(ctx)

        self.voice_connection = await ctx.author.voice.channel.connect()
        await ctx.send(f'Joined voice channel: `{ctx.author.voice.channel.name}`')

    @music.command(help="Pauses audio playback")
    async def pause(self, ctx):
        if not await self.check_bot_voice_connected(ctx):
            return
        if self.voice_connection.is_paused():
            await ctx.send('Bot is already paused')
            return
        self.voice_connection.pause()
        self._pause_time()
        await ctx.send('⏸ Pausing music')

    @music.command(help="Resumes audio playback")
    async def resume(self, ctx):
        if not await self.check_bot_voice_connected(ctx):
            return
        if not self.voice_connection.is_paused():
            ctx.send('The bot is not paused')
            return
        self.voice_connection.resume()
        self._resume_time()
        await ctx.send('▶️ Resuming music')

    @music.command(help="Stops audio playback and clears the queue")
    async def stop(self, ctx):
        if not await self.check_bot_voice_connected(ctx):
            return
        self.queue = []
        self.currently_playing_info = None
        self.voice_connection.stop()
        if ctx: await ctx.send('⏹️ Stopping music and clearing queue')

    @music.command(help="Skips to a certain part of the video. NOT IMPLEMENTED YET")
    async def seek(self, ctx):
        pass

    @music.command(help="Skips to the next in queue")
    async def skip(self, ctx):
        if not await self.check_bot_voice_connected(ctx):
            return
        self.voice_connection.stop()
        await ctx.send('⏭️ Skipping to next in queue')

    @music.command(help="Displays the information of the currently playing video")
    async def np(self, ctx):
        if not await self.check_bot_voice_connected(ctx):
            return
        if not self.voice_connection.is_playing() and not self.voice_connection.is_paused():
            await ctx.send('Nothing is playing at the moment')
            return
        embed = self._get_video_information_embed(self.currently_playing_info, time_stamp=self._get_time())
        await ctx.send(f'', embed=embed)

    @music.command(help="Shows the audio queue. Usage: !queue [page number](optional)")
    async def queue(self, ctx, page: typing.Optional[int] = 1):
        if not await self.check_bot_voice_connected(ctx):
            return
        if not self.queue or not self.currently_playing_info:
            await ctx.send('Queue is empty')
            return

        pages = (len(self.queue) // 10) + 1
        if page > pages:
            page = pages
        elif page < 1:
            page = 1

        embed = discord.Embed(title='Music player queue')
        embed.description = f'**{len(self.queue)}** in queue.\n Currently playing: `{self.currently_playing_info["title"]}`'
        for i in range(10):
            i += (page - 1) * 10
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

    @music.command(help="Leaves the connected voice channel and clears the queue")
    async def leave(self, ctx):
        if not await self.check_bot_voice_connected(ctx):
            return
        await self.stop(None)
        await self.voice_connection.disconnect()
        await ctx.send(f'Leaving voice channel `{self.voice_connection.channel.name}` and clearing queue')
        self.voice_connection = None

    @music.error
    async def music_error(self, ctx, error):
        if isinstance(error, UserNotInVoiceChannel):
            await ctx.send(error)
        elif isinstance(error, BotNotInVoiceChannel):
            await ctx.send(error)
        else:
            print(f'An unexpected error occurred from the command {ctx.message.content}: {error}')
            await ctx.send('There was an error executing this command. Contact a developer if the problem persists')

    def cog_unload(self):
        # TODO: Find a way to disconnect bot when cog is unloaded without it being a coroutine
        # (rare bug causes the bot to keep playing even after the cog is not available)
        pass


def setup(bot):
    if which('ffmpeg') is None:
        raise FileNotFoundError('ffmpeg was not found or is not installed')
    bot.add_cog(MusicPlayer(bot))
