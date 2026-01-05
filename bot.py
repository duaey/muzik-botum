import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from flask import Flask
from threading import Thread
import static_ffmpeg

# koyeb canli tutma
app = Flask('')
@app.route('/')
def home(): return "bot aktif"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run, daemon=True).start()

# kanka ffmpeg yollarini sisteme ekle ve yolunu degiskene ata
static_ffmpeg.add_paths()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

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

    if not ctx.voice_client:
        vc = await ctx.author.voice.channel.connect(timeout=30.0, self_deaf=True)
    else:
        vc = ctx.voice_client

    async with ctx.typing():
        try:
            # kanka direkt ffmpeg komutuyla baslat
            source = discord.FFmpegPCMAudio(search, executable="ffmpeg", **ffmpeg_opts)
            vc.play(source)
            await ctx.send(f'caliyor kanka valla bu sefer oldu: **{search}**')
        except Exception as e:
            await ctx.send(f"hata kanka: {e}")

keep_alive()
bot.run(os.environ.get('TOKEN'))
