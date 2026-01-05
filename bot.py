import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "bot canavar"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run, daemon=True).start()

# kanka baglanti hatasini cozmek icin sese giris mantigini degistirdik
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
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

    # kanka eski baglantiyi zorla kapat
    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        await asyncio.sleep(1)

    try:
        # kanka sese girerken artik daha sabirliyiz
        vc = await ctx.author.voice.channel.connect(timeout=30.0, self_deaf=True)
    except Exception as e:
        # kanka eger hala index hatasi verirse kütüphane sürümü sakat demektir
        return await ctx.send(f"baglanti hatasi (index hatasi ise dc.py guncelle): {e}")

    async with ctx.typing():
        try:
            # kanka eger direkt mp3 linki attiysan youtube'u hic karistirmiyoruz
            if search.endswith('.mp3'):
                source_url = search
                title = "MP3 Dosyasi"
            else:
                # kanka youtube engeli varsa burasi patlar o yuzden buraya ozel kontrol
                with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch1:{search}", download=False)['entries'][0]
                    source_url = info['url']
                    title = info['title']
            
            source = discord.FFmpegPCMAudio(source_url, executable='ffmpeg', **ffmpeg_opts)
            vc.play(source)
            await ctx.send(f'caliyor kanka: **{title}**')
        except Exception as e:
            await ctx.send(f"hata cikti kanka: {e}")

keep_alive()
bot.run(os.environ.get('TOKEN'))
