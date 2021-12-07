import discord
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import CommandNotFound
import youtube_dl
app = commands.Bot(command_prefix='.')


@app.event
async def on_ready():
    await app.change_presence(status=discord.Status.online, activity=None)
    # 채널 메시지 보내기
    # for guild in app.guilds:
    #     print(guild.id)
    #     if str(guild.id) == '838595214205255680':
    #         await guild.text_channels[0].send('test')
    #         break;

@app.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error
@app.event
async def on_voice_state_update(a,b,c):
    if not c.channel:
        if me:
            list = []
            embed = me[0].embeds[0].to_dict()
            embed['description'] = '노래 컨트롤러'
            embed = discord.Embed.from_dict(embed)
            embed.set_image(url="https://i.imgur.com/X5ECwa0.png")
            await me[0].edit(embed=embed)
@app.event
async def on_message(message):
    if message.content.startswith('.셋업'):
        embed = discord.Embed(title="깜언 노래 봇", description="노래 컨트롤러", color=0x00aaaa)
        embed.set_image(url="https://i.imgur.com/X5ECwa0.png")
        m = await message.channel.send(embed=embed)
        await m.add_reaction("⏸")
        await m.add_reaction("⏹")
        await m.add_reaction("▶")
        await m.add_reaction("⏭")
        await m.add_reaction("❌")

    if message.author.id == app.user.id:
        return
    if str(message.channel) == '노래요청':
        await message.delete()
        if message.content.startswith('https://www.youtube.com/'):
            ydl_opts = {  # 다운로드 옵션
                'format': 'bestaudio'
            }
            global list
            global voice
            global me
            list = []
            msgs = message
            if not message.guild.voice_client :
                await message.author.voice.channel.connect()
            msg_index = message.content.find('list')
            if not msg_index == -1:
                msg = message.content[:msg_index-1]
            else:
                msg = message.content
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(msg, download=False)
                URL = info['formats'][0]['url']
            voice = message.guild.voice_client
            list.append(URL)
            me = False
            if not voice.is_playing():
                musicplay()
                me = await msgs.channel.history(limit=1, oldest_first=True).flatten()
                embed = me[0].embeds[0].to_dict()
                embed['description'] = info['title']
                embed = discord.Embed.from_dict(embed)
                embed.set_image(url=info['thumbnail'])
                await me[0].edit(embed=embed)
        else:
            await message.channel.send('유효한 주소가 아닙니다.', delete_after=3)
            return


@app.event
async def on_raw_reaction_add(payload):
    voiceCh = False
    channel = await app.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = await app.fetch_user(payload.user_id)
    reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
    if voice:
        if str(reaction.emoji) == "⏸":
            voice.pause()
        if str(reaction.emoji) == "▶":
            voice.resume()
        if str(reaction.emoji) == "⏹":
            voice.stop()
        if str(reaction.emoji) == "❌":
            await voice.disconnect()
        if str(reaction.emoji) == "⏭":
            voice.stop()
            musicplay()
    await reaction.remove(payload.member)

def musicplay(after=""):
    global list
    global voice
    global msgs
    if list:
        url = list[0]
        del list[0]
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        voice.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=musicplay)



app.run('ODg4OTQ1Njc1NTMyOTI2OTk3.YUaFLA.2pyD0JLfYZQ8lkGiqbaDkJZtBuE')