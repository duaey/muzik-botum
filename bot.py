import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import static_ffmpeg
static_ffmpeg.add_paths()

# --- KOYEB ICIN YALANCI WEB SUNUCUSU ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check():
    server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
    server.serve_forever()

# Sunucuyu arka planda baslat
threading.Thread(target=run_health_check, daemon=True).start()
# --------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'nocheckcertificate': True, 'quiet': True}
ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@bot.event
async def on_ready():
    print(f'bot koyebe yerlesti kanka: {bot.user}')

@bot.command()
async def cal(ctx, *, url):
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        ctx.voice_client.play(discord.FFmpegPCMAudio(url2, **ffmpeg_opts))
    await ctx.send(f'caliyorum: {info["title"]}')

bot.run(os.environ.get('TOKEN'))

