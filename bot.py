import discord
from discord.ext import commands
import yt_dlp
import os
import static_ffmpeg
from static_ffmpeg import run
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ffmpeg setup
static_ffmpeg.add_paths()
try:
    FFMPEG_EXE = run.get_or_fetch_platform_executables_else_raise()[0]
except:
    FFMPEG_EXE = "ffmpeg"

# health check server for koyeb
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is online")

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 8080), HealthCheckHandler).serve_forever(), daemon=True).start()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

# bu ayarlar seste takilmayi ve youtube engelini onler
ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

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
    
    if not ctx.voice_client:
        # ses paketleri gitsin diye self_deaf kapali kalsin
        await ctx.author.voice.channel.connect(self_deaf=False)
    
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                # sesin discorda ulasmasi icin pcm audio kullaniyoruz
                source = discord.FFmpegPCMAudio(url2, executable=FFMPEG_EXE, **ffmpeg_opts)
                ctx.voice_client.play(source)
                await ctx.send(f'now playing: **{info["title"]}**')
        except Exception as e:
            await ctx.send(f"hata kanka: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("bye bye")

bot.run(os.environ.get('TOKEN'))
