import discord
from discord.ext import commands
import yt_dlp
import os
import static_ffmpeg
from static_ffmpeg import run
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ffmpeg ayari
static_ffmpeg.add_paths()
try:
    FFMPEG_EXE = run.get_or_fetch_platform_executables_else_raise()[0]
except:
    FFMPEG_EXE = "ffmpeg"

# health check kismi (koyeb icin sart)
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

ytdl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True, 'no_warnings': True}
# kanka buradaki -reconnect ayarlari sesin kesilmemesini saglar
ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@bot.event
async def on_ready():
    print(f'bot is online kanka: {bot.user}')

@bot.command()
async def play(ctx, *, url):
    if not ctx.author.voice:
        return await ctx.send("get in a voice channel first bro")
    
    if not ctx.voice_client:
        # kanka baglanirken self_deaf kapali olsun bazen o da sorun cikariyor
        await ctx.author.voice.channel.connect(self_deaf=False)
    
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    async with ctx.typing():
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
            # kanka direkt pcm audio kullanarak kütüphane riskini azaltiyoruz
            source = discord.FFmpegPCMAudio(url2, executable=FFMPEG_EXE, **ffmpeg_opts)
            ctx.voice_client.play(source)
    
    await ctx.send(f'now playing: **{info["title"]}**')

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("bye bye")

bot.run(os.environ.get('TOKEN'))
