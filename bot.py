import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import static_ffmpeg

# kanka ffmpeg'i burada hazirliyoruz ki bot baslarken yolunu bulsun
static_ffmpeg.add_paths()
FFMPEG_PATH = static_ffmpeg.run.get_ffmpeg_bin()

# Koyeb canli tutma servisi
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"bot canavar gibi calisiyor kanka")

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 8080), HealthCheckHandler).serve_forever(), daemon=True).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

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
        return await ctx.send("once sese gir kanka")
    
    # baglanti varsa temizle baştan baglan (4006 savar)
    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await asyncio.sleep(1)
    
    try:
        vc = await ctx.author.voice.channel.connect(timeout=20.0, self_deaf=True)
    except Exception as e:
        return await ctx.send(f"sese girerken patladik: {e}")
    
    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                
                audio_url = info['url']
                
                # kanka asil olay burada yolu elle veriyoruz
                source = discord.FFmpegPCMAudio(
                    audio_url, 
                    executable=FFMPEG_PATH, 
                    **ffmpeg_opts
                )
                
                vc.play(source)
                await ctx.send(f'su an caliyor kanka: **{info["title"]}**')
        except Exception as e:
            await ctx.send(f"oynatırken hata cikti: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("kactim kanka hadi eyvallah")

# kanka tokeni koyeb env kismina TOKEN olarak eklemeyi unutma
bot.run(os.environ.get('TOKEN'))
