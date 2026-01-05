import discord
from discord.ext import commands
import yt_dlp
import os
import static_ffmpeg
from static_ffmpeg import run
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import asyncio

# ffmpeg setup
static_ffmpeg.add_paths()
try:
    FFMPEG_EXE = run.get_or_fetch_platform_executables_else_raise()[0]
except:
    FFMPEG_EXE = "ffmpeg"

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 8080), HealthCheckHandler).serve_forever(), daemon=True).start()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}
ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@bot.event
async def on_ready():
    print(f'bot online kanka: {bot.user}')

@bot.command()
async def play(ctx, *, url):
    if not ctx.author.voice:
        return await ctx.send("get in a voice channel first")
    
    # 4006 hatasini temizlemek icin eski baglantiyi silip 2 saniye bekletiyoruz
    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await asyncio.sleep(2)

    try:
        # kanka 4006 hatasini onlemek icin self_deaf=True yapalim bu cok onemli
        vc = await ctx.author.voice.channel.connect(timeout=60.0, self_deaf=True)
    except Exception as e:
        return await ctx.send(f"connection error: {e}")

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                source = discord.FFmpegPCMAudio(url2, executable=FFMPEG_EXE, **ffmpeg_opts)
                vc.play(source)
                await ctx.send(f'now playing: **{info["title"]}**')
        except Exception as e:
            await ctx.send(f"playback error: {e}")

bot.run(os.environ.get('TOKEN'))
