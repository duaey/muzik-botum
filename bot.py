import discord
from discord.ext import commands
import yt_dlp
import os
import static_ffmpeg
from static_ffmpeg import run
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import asyncio

# ffmpeg tam yolunu zorlayalim
static_ffmpeg.add_paths()
try:
    FFMPEG_EXE = run.get_or_fetch_platform_executables_else_raise()[0]
except:
    FFMPEG_EXE = "ffmpeg"

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot online kanka")

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 8080), HealthCheckHandler).serve_forever(), daemon=True).start()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'bot online: {bot.user}')

@bot.command()
async def play(ctx, *, url):
    if not ctx.author.voice:
        return await ctx.send("once sese gir kanka")
    
    # 4006 hatasini onlemek icin varsa eski baglantiyi tamamen kopar
    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await asyncio.sleep(1)

    try:
        # kendi kendine sagirlastirmayi (self_deaf) true yapalim stabilite artar
        vc = await ctx.author.voice.channel.connect(self_deaf=True)
    except Exception as e:
        return await ctx.send(f"baglanti hatasi kanka: {e}")

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                # -11 hatasini onlemek icin en basit pcm audio
                source = discord.FFmpegPCMAudio(url2, executable=FFMPEG_EXE, **ffmpeg_opts)
                vc.play(source)
                await ctx.send(f'caliyor: **{info["title"]}**')
        except Exception as e:
            await ctx.send(f"oynatma hatasi: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await ctx.send("ciktim kanka")

bot.run(os.environ.get('TOKEN'))
