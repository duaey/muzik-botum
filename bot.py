import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import static_ffmpeg
from static_ffmpeg import run

# setup ffmpeg path correctly
static_ffmpeg.add_paths()
try:
    FFMPEG_EXE = run.get_or_fetch_platform_executables_else_raise()[0]
except:
    FFMPEG_EXE = "ffmpeg"

# koyeb health check server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_health_check():
    server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check, daemon=True).start()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
}

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'bot is online: {bot.user}')

@bot.command()
async def play(ctx, *, url):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            return await ctx.send("you need to be in a voice channel first")
    
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                
                # using standard FFmpegPCMAudio for stability
                source = discord.FFmpegPCMAudio(url2, executable=FFMPEG_EXE, **ffmpeg_opts)
                ctx.voice_client.play(source)
                await ctx.send(f'now playing: **{info["title"]}**')
        except Exception as e:
            await ctx.send(f"an error occurred: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("disconnected")
    else:
        await ctx.send("i am not in a voice channel")

bot.run(os.environ.get('TOKEN'))
