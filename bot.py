import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from flask import Flask
from threading import Thread

# flask kanka (koyeb uyutmasin diye)
app = Flask('')
@app.route('/')
def home(): return "canavar gibi calisiyor kanka"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run, daemon=True).start()

# kanka intents ayarlarini dibine kadar actim (portal'dan da acmayi unutma)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'bot hazir kanka: {bot.user}')

@bot.command()
async def play(ctx, *, search: str):
    # sese baglanma kanka
    if not ctx.author.voice:
        return await ctx.send("once sese gir kanka")
    
    if not ctx.voice_client:
        vc = await ctx.author.voice.channel.connect(timeout=20, self_deaf=True)
    else:
        vc = ctx.voice_client

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                # kanka arama sonucunu oyle bi cekiyoruz ki hata payi kalmiyor
                info = ydl.extract_info(f"ytsearch1:{search}", download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]
                
                url = info['url']
                
                if vc.is_playing():
                    vc.stop()
                
                # kanka artik direkt sistemdeki ffmpeg'i kullaniyoruz
                source = discord.FFmpegPCMAudio(url, **ffmpeg_opts)
                vc.play(source)
                await ctx.send(f'caliyor kanka: **{info["title"]}**')
                
        except Exception as e:
            print(f"hata detayi kanka: {e}")
            await ctx.send(f"hata kanka valla patladik: {e}")

# kanka tokeni os'tan cekiyoruz
keep_alive()
bot.run(os.environ.get('TOKEN'))
