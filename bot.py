import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# kanka botun kapanmamasi icin health check sart
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"bot online kanka")

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 8080), HealthCheckHandler).serve_forever(), daemon=True).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True, 'default_search': 'auto'}
ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@bot.event
async def on_ready():
    print(f'bot online kanka: {bot.user}')

@bot.command()
async def play(ctx, *, url):
    if not ctx.author.voice:
        return await ctx.send("once sese gir kanka")
    
    # kanka 4006 hatasini asmak icin her play'de baglantiyi yeniliyoruz
    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await asyncio.sleep(1)

    try:
        # kanka sese baglanirken gateway'i kandirmak icin deaf modu acik giriyoruz
        vc = await ctx.author.voice.channel.connect(timeout=20.0, self_deaf=True)
    except Exception as e:
        return await ctx.send(f"baglanti patladi: {e}")

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info: info = info['entries'][0]
                url2 = info['url']
                source = discord.FFmpegPCMAudio(url2, **ffmpeg_opts)
                vc.play(source)
                await ctx.send(f'caliyor kanka: **{info["title"]}**')
        except Exception as e:
            await ctx.send(f"hata var: {e}")

bot.run(os.environ.get('TOKEN'))
