import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from flask import Flask
from threading import Thread
import static_ffmpeg # kanka bu sart

# koyeb yasam destegi
app = Flask('')
@app.route('/')
def home(): return "bot canavar gibi"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run, daemon=True).start()

# kanka ffmpeg'i baslatiyoruz
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

    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await asyncio.sleep(1)

    try:
        vc = await ctx.author.voice.channel.connect(timeout=30.0, self_deaf=True)
    except Exception as e:
        return await ctx.send(f"baglanti hatasi: {e}")

    async with ctx.typing():
        try:
            # kanka mp3 linki ise direkt calistiriyoruz
            source = discord.FFmpegPCMAudio(search, **ffmpeg_opts)
            # ses seviyesini sabitle kanka
            source = discord.PCMVolumeTransformer(source, volume=0.8)
            
            vc.play(source, after=lambda e: print(f'bitti hata: {e}') if e else None)
            await ctx.send(f'caliyor kanka: **{search}**')
        except Exception as e:
            await ctx.send(f"hata kanka: {e}")

keep_alive()
bot.run(os.environ.get('TOKEN'))
