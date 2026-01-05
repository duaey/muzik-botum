import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from flask import Flask
from threading import Thread
import subprocess

# kanka flask ile koyeb'i uyutuyoruz
app = Flask('')
@app.route('/')
def home():
    return "kanka bot yasiyor sıkıntı yok"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# kanka ffmpeg'i sistemde bulamazsa static-ffmpeg'den zorla cekiyoruz
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
    # kanka yeni versiyonda bu sekilde cagrilir
    FFMPEG_PATH = "ffmpeg" 
except:
    FFMPEG_PATH = "ffmpeg"

intents = discord.Intents.all()
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
    print(f'bot online kanka: {bot.user}')

@bot.command()
async def play(ctx, *, url):
    if not ctx.author.voice:
        return await ctx.send("once sese gir kanka")
    
    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await asyncio.sleep(1)
    
    try:
        vc = await ctx.author.voice.channel.connect(timeout=30.0, self_deaf=True)
    except Exception as e:
        return await ctx.send(f"sese girerken patladik: {e}")
    
    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info: info = info['entries'][0]
                audio_url = info['url']
                
                # kanka burasi artik hata vermez
                source = discord.FFmpegPCMAudio(audio_url, executable=FFMPEG_PATH, **ffmpeg_opts)
                vc.play(source)
                await ctx.send(f'caliyor kanka: **{info["title"]}**')
        except Exception as e:
            await ctx.send(f"hata kanka: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("kactim kanka")

keep_alive()
bot.run(os.environ.get('TOKEN'))
