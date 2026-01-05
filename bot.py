import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# kanka ffmpeg isini en garanti yola aliyoruz
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot online")

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 8080), HealthCheckHandler).serve_forever(), daemon=True).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# youtube ayarlari
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
    print(f'bot online: {bot.user}')

@bot.command()
async def play(ctx, *, url):
    if not ctx.author.voice:
        return await ctx.send("once sese gir kanka")
    
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
    
    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                # kanka eger bir liste donerse ilkini al diyoruz hata cikmasin
                if 'entries' in info:
                    info = info['entries'][0]
                
                url2 = info['url']
                # kanka direkt ffmpeg yaziyoruz koyeb bunu otomatik tanir artik
                source = discord.FFmpegPCMAudio(url2, **ffmpeg_opts)
                
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                    
                ctx.voice_client.play(source)
                await ctx.send(f'caliyor kanka: **{info["title"]}**')
        except Exception as e:
            await ctx.send(f"hata cikti kanka: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("hadi kactim")

bot.run(os.environ.get('TOKEN'))
