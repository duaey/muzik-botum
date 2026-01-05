import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from flask import Flask
from threading import Thread

# koyeb canli tutma
app = Flask('')
@app.route('/')
def home(): return "bot canavar"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run, daemon=True).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'nocheckcertificate': True
}

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'bot online: {bot.user}')

@bot.command()
async def play(ctx, *, search):
    if not ctx.author.voice:
        return await ctx.send("once sese gir kanka")

    # kanka eski baglantiyi temizle
    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await asyncio.sleep(1)

    try:
        # kanka bu baglanti satiri discord'un yeni guncellemesine uygun
        vc = await ctx.author.voice.channel.connect(timeout=20.0, self_deaf=True)
    except Exception as e:
        return await ctx.send(f"baglanti hatasi: {e}")

    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{search}", download=False)['entries'][0]
                url = info['url']
                
                # kanka ffmpeg sistemde Aptfile ile yuklendi artik
                source = discord.FFmpegPCMAudio(url, executable='ffmpeg', **ffmpeg_opts)
                vc.play(source)
                await ctx.send(f'caliyor kanka: **{info["title"]}**')
        except Exception as e:
            await ctx.send(f"oynatma hatasi: {e}")

keep_alive()
bot.run(os.environ.get('TOKEN'))
