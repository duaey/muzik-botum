import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_format_options = {'format': 'bestaudio/best', 'noplaylist': True, 'nocheckcertificate': True, 'quiet': True, 'no_warnings': True, 'default_search': 'auto', 'source_address': '0.0.0.0'}
ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data: data = data['entries'][0]
        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)

@bot.event
async def on_ready(): print(f'bot online: {bot.user}')

@bot.command()
async def cal(ctx, *, url):
    if not ctx.voice_client: await ctx.author.voice.channel.connect()
    player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
    ctx.voice_client.play(player)
    await ctx.send(f'caliniyor: {player.title}')

@bot.command()
async def dur(ctx):
    if ctx.voice_client: await ctx.voice_client.disconnect()

bot.run(os.getenv('TOKEN')) # burası böyle kalsın tokeni siteye yazacağız