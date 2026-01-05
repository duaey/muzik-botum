import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from flask import Flask
from threading import Thread

# kanka flask ile koyeb'i kandiriyoruz
app = Flask('')
@app.route('/')
def home():
    return "kanka bot yasiyor sorun yok"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# kanka yt-dlp ayarlarini en saglam hale getirdim
ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# kanka ffmpeg ayarlarini kopma yapmayacak sekilde ayarladim
ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'bot online kanka: {bot.user}')

@bot.command()
async def play(ctx, *, search):
    if not ctx.author.voice:
        return await ctx.send("once sese gir kanka")
    
    # baglan kanka
    if not ctx.voice_client:
        try:
            vc = await ctx.author.voice.channel.connect(timeout=30.0, self_deaf=True)
        except Exception as e:
            return await ctx.send(f"baglanirken patladik: {e}")
    else:
        vc = ctx.voice_client

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                # kanka arama sonucunu aliyoruz
                info = ydl.extract_info(f"ytsearch1:{search}", download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                
                url = info['url']
                
                if vc.is_playing():
                    vc.stop()
                
                # kanka ffmpeg'i direkt sistemden 'ffmpeg' olarak cagiriyoruz
                source = discord.FFmpegPCMAudio(url, executable='ffmpeg', **ffmpeg_opts)
                vc.play(source)
                await ctx.send(f'caliyor kanka: **{info["title"]}**')
        except Exception as e:
            await ctx.send(f"hata kanka: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("kactim kanka")

# kanka calistiriyoruz
keep_alive()
bot.run(os.environ.get('TOKEN'))
