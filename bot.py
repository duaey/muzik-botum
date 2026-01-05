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
        self.wfile.write(b"Bot is alive")

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 8080), HealthCheckHandler).serve_forever(), daemon=True).start()

# intents ayarlarini en genis hale getirdik
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}
ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'bot online kanka: {bot.user}')

@bot.command()
async def play(ctx, *, url):
    if not ctx.author.voice:
        return await ctx.send("get in a voice channel first")
    
    # varsa eski bozuk baglantiyi zorla kapat
    if ctx.voice_client:
        try:
            await ctx.voice_client.disconnect(force=True)
        except:
            pass
        await asyncio.sleep(2)

    try:
        # baglanti sirasinda 4006'yi onlemek icin self_deaf ve self_mute kapali kalsin
        vc = await ctx.author.voice.channel.connect(timeout=60.0, self_deaf=False, self_mute=False)
    except Exception as e:
        return await ctx.send(f"baglanti patladi kanka: {e}")

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                source = discord.FFmpegPCMAudio(url2, executable=FFMPEG_EXE, **ffmpeg_opts)
                vc.play(source)
                await ctx.send(f'caliyor: **{info["title"]}**')
        except Exception as e:
            await ctx.send(f"oynatma hatasi: {e}")

bot.run(os.environ.get('TOKEN'))
