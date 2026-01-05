import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from flask import Flask
from threading import Thread
import static_ffmpeg

# Flask ve keep_alive kısımları aynı kanka bozma
app = Flask('')
@app.route('/')
def home(): return "bot aktif kanka"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# kanka ffmpeg'i zorla kurdurup yolunu alıyoruz
static_ffmpeg.add_paths()
FFMPEG_PATH = "ffmpeg"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# kanka yt-dlp ayarlarını en basite çektim ki hata vermesin
ytdl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'nocheckcertificate': True,
}

# kanka bu ffmpeg ayarları yayını canlı tutar
ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

@bot.event
async def on_ready():
    print(f'bot online kanka: {bot.user}')

@bot.command()
async def play(ctx, *, search):
    if not ctx.author.voice:
        return await ctx.send("once sese gir kanka")
    
    # baglanma isi kanka
    if not ctx.voice_client:
        try:
            vc = await ctx.author.voice.channel.connect(timeout=20.0, self_deaf=True)
        except Exception as e:
            return await ctx.send(f"baglanti hatasi: {e}")
    else:
        vc = ctx.voice_client

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                # kanka arama yaparken daha garantici davranıyoruz
                info = ydl.extract_info(f"ytsearch1:{search}", download=False)['entries'][0]
                url = info['url']
                
                # kanka eski source'u temizle
                if vc.is_playing():
                    vc.stop()
                
                # asıl olay burada kanka FFmpegPCMAudio'yu en stabil hale getirdik
                source = discord.FFmpegPCMAudio(url, executable=FFMPEG_PATH, **ffmpeg_opts)
                
                # kanka sesi sarmalamak (wrap) bazen hayat kurtarır
                vc.play(discord.PCMVolumeTransformer(source, volume=1.0))
                await ctx.send(f'caliyor kanka: **{info["title"]}**')
                
        except Exception as e:
            await ctx.send(f"hata kanka: {e}")

keep_alive()
bot.run(os.environ.get('TOKEN'))
