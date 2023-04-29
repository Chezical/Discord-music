import discord
from discord.ext import commands
import youtube_dl

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

# Define options for the audio stream downloader
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'source_address': '0.0.0.0'
}

# Define the Discord client and command prefix
client = commands.Bot(command_prefix='!')

# Define the function for playing audio streams
def play_audio(ctx, url):
    # Set up the audio stream downloader
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']

    # Join the voice channel of the command invoker
    voice_channel = ctx.message.author.voice.channel
    voice_client = ctx.message.guild.voice_client
    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await voice_client.move_to(voice_channel)

    # Start playing the audio stream
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(URL))
    voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
    voice_client.source = discord.PCMVolumeTransformer(source, volume=0.5)

# Define the play command for the bot
@client.command(name='play')
async def play(ctx, *, url):
    # Check if the command invoker is in a voice channel
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return

    # Check if the bot has permission to join and speak in the voice channel
    permissions = ctx.message.author.voice.channel.permissions_for(ctx.message.guild.me)
    if not permissions.connect:
        await ctx.send("I cannot connect to your voice channel.")
        return
    elif not permissions.speak:
        await ctx.send("I cannot speak in your voice channel.")
        return

    # Start playing the audio stream
    await play_audio(ctx, url)

# Define the stop command for the bot
@client.command(name='stop')
async def stop(ctx):
    # Stop playing audio and disconnect from the voice channel
    voice_client = ctx.message.guild.voice_client
    if voice_client is not None:
        voice_client.stop()
        await voice_client.disconnect()

# Run the bot with the specified token
client.run('MTEwMTk2OTg5MjM5NzI5NzY2NA.GyaccC.en1kpus7PL4fsZQJNhO3IkmfmSDJi1_63kGvV0')
