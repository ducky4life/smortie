import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
import keep_alive
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import random
import music_tag
from dotenv import load_dotenv

intents = discord.Intents.all()
intents.members = True

load_dotenv()

bot_prefix = "smorts"
codespace = "actionss"


if bot_prefix == "smort":
    token = os.getenv("SMORT_TOKEN")
else:
    token = os.getenv("ROBO_TOKEN")

if codespace == "github":
    rootpath = "/workspaces"
elif codespace == "actions":
    rootpath = "/home/runner/work/smortie"
else:
    rootpath = "c:/Users/ducky/Documents"



client = commands.Bot(
    command_prefix=[f"!{bot_prefix} ", f"!{bot_prefix} "],
    intents=intents)

async def send_codeblock(ctx, msg):
    if len(msg) > 1993:
        if len(msg) > 3993:
            first_msg = msg[:1993]
            second_msg = msg[1993:3993].strip()
            third_msg = msg[3993:].strip()
            await ctx.send(f"```{first_msg}```")
            await ctx.send(f"```{second_msg}```")
            await ctx.send(f"```{third_msg}```")
        else:
            first_msg = msg[:1993]
            second_msg = msg[1993:].strip()
            await ctx.send(f"```{first_msg}```")
            await ctx.send(f"```{second_msg}```")
    else:
        await ctx.send(f"```{msg}```")


@client.event
async def on_ready():
    print('Roboduck is ready')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="ITS SHAUN THE SHEEP!"))
    await client.tree.sync()




# music stuffs

@client.hybrid_command(description="plays a playlist given a vc id and playlist name", brief="plays a playlist")
@app_commands.describe(playlist="wat i play", shuffle="say shuffle if yes")
@app_commands.choices(shuffle=[
    app_commands.Choice(name='shuffle', value="shuffle"),
    app_commands.Choice(name='no', value="no")
])
async def play(ctx, channel: discord.VoiceChannel, playlist=None, shuffle=None):

    folder_path = f"{rootpath}/smortie/playlists/{playlist}"
    print(folder_path)

    # check if playlist exists
    if playlist == "master":
        await ctx.send("ok playing all songs")
        folder_path = f"{rootpath}/smortie/playlists"
    elif playlist == "continue":
        await ctx.send("ok i continue")
        folder_path = f"{rootpath}/smortie/playlists"
    elif playlist == None:
        await ctx.send("no playlist? ok i play queue")
        folder_path = f"{rootpath}/smortie/playlists/queue"
        playlist = "queue"

    elif os.path.isdir(folder_path) == False:
        await ctx.send("umm i cant find the playlist :( i play queue)")
        folder_path = f"{rootpath}/smortie/playlists/queue"
        playlist = "queue"

    else:
        await ctx.send(f"found ur playlist yay!!! playing {playlist}")
        folder_path = f"{rootpath}/smortie/playlists/{playlist}"
    

    music_files = os.listdir(folder_path)


    # master: add all songs to music_files
    if playlist == "master":
        music_files = ""
        for path, subdirs, files in os.walk(folder_path):
            for name in files:
                if name in music_files:
                    ctx.send(name)
                else:
                    music_files += f'{os.path.join(path, name)}?'.removeprefix(folder_path)
        music_files = music_files.split("?")

    # continue: get queue from queue.txt
    elif playlist == "continue":
        with open("queue.txt", encoding="utf-8") as file:
            music_files = file.readlines()
            music_files = [song.strip() for song in music_files]  # Strip newline characters


    # check if shuffle is enabled
    if shuffle == None:
        await ctx.send("no shuffle mode, i go alphabetical")
    elif shuffle.lower() == "shuffle":
        await ctx.send("shuffle mode go brr")
        random.shuffle(music_files)



    # write all songs to queue.txt
    dupe_music_files = music_files.copy()

    if playlist == "master":
        with open("queue.txt", "w", encoding="utf-8") as file:
            for music in dupe_music_files:
                if music == "\n" or music == "":
                    dupe_music_files.remove(music)
            file.write("\n".join(dupe_music_files))

    # write songs in playlist to queue.txt
    elif playlist != "continue":
        with open("queue.txt", "w", encoding="utf-8") as file:
            music_files_with_playlist_path = [f"/{playlist}/{song}" for song in dupe_music_files]
        
            file.write("\n".join(music_files_with_playlist_path))



    # get channel
    channel_id = channel.id
    channel = client.get_channel(channel_id)
    if not channel:
        await ctx.send("um can u giv me a valid voice channel id pls")




    # actual playing code
    voice_client = await channel.connect()
    dupe_music_files_2 = music_files.copy()


    for i in range(len(music_files)):
        music_files = [file.replace("\\", '/') for file in music_files]



        # master playlist
        if playlist == "master":
            file_to_load = f"playlists{music_files[i]}"
            full_file_path = f'{folder_path}{music_files[i]}'
            file_to_play = f'playlists{music_files[i]}'
            queue_list = dupe_music_files_2



        # continue playlist
        elif playlist == "continue":
            file_to_load = f"playlists{music_files[i]}"
            full_file_path = f'{folder_path}{music_files[i]}'
            file_to_play = f'playlists{music_files[i]}'
            queue_list = dupe_music_files_2
            music_files[i] = music_files[i].strip()



        # non master playlist
        else:
            file_to_load = f"playlists/{playlist}/{music_files[i]}"
            full_file_path = f"{folder_path}/{music_files[i]}"
            file_to_play = f"playlists/{playlist}/{music_files[i]}"
            queue_list = music_files_with_playlist_path


        f = music_tag.load_file(file_to_load)
        title = f['title']
        if music_files[i].endswith(".mp3"):
            time = MP3(full_file_path).info.length + 3
        else:
            time = MP4(full_file_path).info.length + 3

        async def sleep_until_song_ends(time):
            await asyncio.sleep(time)

        class Buttons(discord.ui.View):
            @discord.ui.button(label='pause', style=discord.ButtonStyle.success)
            async def pause(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
                voice_client.pause()
                await interaction.response.send_message('ok i wait')
            @discord.ui.button(label='resume', style=discord.ButtonStyle.success)
            async def resume(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
                voice_client.resume()
                await interaction.response.send_message('yay i sing')
            @discord.ui.button(label='skip', style=discord.ButtonStyle.secondary)
            async def skip(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
                task.cancel()
                await interaction.response.edit_message(content='i sing next song', view=None)
            @discord.ui.button(label='queue', style=discord.ButtonStyle.secondary)
            async def displayqueue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
                with open("queue.txt", encoding="utf-8") as queue_file:
                    msg = ""
                    for row in queue_file:
                        if row != "\n":
                            msg += row
                    if len(msg) > 1993:
                        if len(msg) > 3993:
                            first_msg = msg[:1993]
                            second_msg = msg[1993:3993].strip()
                            third_msg = msg[3993:].strip()
                            await interaction.response.send_message(f"```{first_msg}```")
                            await interaction.response.send_message(f"```{second_msg}```")
                            await interaction.response.send_message(f"```{third_msg}```")
                        else:
                            first_msg = msg[:1993]
                            second_msg = msg[1993:].strip()
                            await interaction.response.send_message(f"```{first_msg}```")
                            await interaction.response.send_message(f"```{second_msg}```")
                    else:
                        await interaction.response.send_message(f"```{msg}```")
            @discord.ui.button(label='stop', style=discord.ButtonStyle.red)
            async def stop(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
                await voice_client.disconnect()
                await interaction.response.edit_message(content='bai bai', view=None)

        voice_client.play(discord.FFmpegPCMAudio(file_to_play))
        await ctx.send(f"playing {title} - {f['artist']}", silent=True, view=Buttons(timeout=None))
        if i < len(music_files)-1:
            queue_list.pop(0)
        with open("queue.txt", "w", encoding="utf-8") as file:
            file.write("\n".join(queue_list))

        task = asyncio.create_task(sleep_until_song_ends(time))
        try:
            await task
            voice_client.stop()
            i = i + 1
            if i == len(music_files):
                await voice_client.disconnect()
                await ctx.send("bai bai")
        except asyncio.CancelledError:
            voice_client.stop()
            i = i + 1
            if i == len(music_files):
                await voice_client.disconnect()
                await ctx.send("bai bai")




@client.hybrid_command(description="plays a file 24/7")
@app_commands.describe(file="wat file i sing? pls include path and file extension")
async def play24(ctx, *, file="sheep.mp3"):
    channel_id = 1132046013360779434
    folder_path = f"{rootpath}/smortie/playlists"
    file_path = f"{folder_path}/{file}"

    if file.endswith(".mp3"):
        time = MP3(f'{folder_path}/{file}').info.length + 3
    else:
        time = MP4(f'{folder_path}/{file}').info.length + 3

    channel = client.get_channel(channel_id)
    if not channel:
        return print('Invalid voice channel ID.')

    voice_client = await channel.connect()
    await ctx.send(f"playing {file} 24/7. please disconnect me from the voice channel if you want to play something else :D")

    while True:
        voice_client.play(discord.FFmpegPCMAudio(file_path))
        await asyncio.sleep(time)
        voice_client.stop()



@client.hybrid_command(description="plays a file once")
async def playfile(ctx, channel: discord.VoiceChannel, *, file=None):
    channel_id = channel.id
    folder_path = f"{rootpath}/smortie/playlists"
    file_path = f"{folder_path}/{file}"

    if file.endswith(".mp3"):
        time = MP3(f'{folder_path}/{file}').info.length + 3
    else:
        time = MP4(f'{folder_path}/{file}').info.length + 3

    channel = client.get_channel(channel_id)
    if not channel:
        return print('Invalid voice channel ID.')

    voice_client = await channel.connect()
    await ctx.send(f"playing {file} :D ill disconnect when its done")

    voice_client.play(discord.FFmpegPCMAudio(file_path))
    await asyncio.sleep(time)
    await voice_client.disconnect()
    await ctx.send("bai bai")



@client.hybrid_command()
async def playlocalfile(ctx, channel: discord.VoiceChannel, file: discord.Attachment):
    await ctx.defer()
    channel_id = channel.id
    folder_path = f"{rootpath}/smortie/playlists/local"
    file_path = f"{folder_path}/{file.filename}"
    if not os.path.exists("playlists/local"):
        os.makedirs("playlists/local")
    await file.save(file_path)

    if file.filename.endswith(".mp3"):
        time = MP3(f'{folder_path}/{file.filename}').info.length + 3
    else:
        time = MP4(f'{folder_path}/{file.filename}').info.length + 3

    channel = client.get_channel(channel_id)
    if not channel:
        return print('Invalid voice channel ID.')

    voice_client = await channel.connect()
    await ctx.send(f"playing {file.filename} :D ill disconnect when its done")

    voice_client.play(discord.FFmpegPCMAudio(file_path))
    await asyncio.sleep(time)
    await voice_client.disconnect()
    await ctx.send("bai bai")




@client.hybrid_command(aliases=['playlist'])
@app_commands.describe(playlist="wat u si")
async def playlists(ctx, *, playlist=None):
    
    if playlist == None:
        playlists = os.listdir(f"{rootpath}/smortie/playlists")
        playlists = '\n'.join(playlists)
        await ctx.send(f"playlists:\n{playlists}\n\nuse !smort play <playlist> to play a playlist, or !smort playlists <playlist> to list the songs in a playlist")
  
    else:
        songs = os.listdir(f"{rootpath}/smortie/playlists/{playlist}")
        new_songs: str = ""
        for song in songs:
            f = music_tag.load_file(f"playlists/{playlist}/{song}")
            new_songs += f"{f['title']} - {str(f['artist']).split(',')[0]} ({song.split('.')[1]})\n"
            msg = f"songs in {playlist}:\n{new_songs}"
        await send_codeblock(ctx, msg)



@client.hybrid_command(aliases=['q'])
async def queue(ctx):
    with open("queue.txt", encoding="utf-8") as queue_file:
        msg = ""
        for row in queue_file:
            if row != "\n":
                msg += row
        await send_codeblock(ctx, msg)



@client.hybrid_command(aliases=['import'])
@app_commands.describe(queue="wat i nom")
async def importqueue(ctx, *, queue=None):
    if queue == None:
        await ctx.send("no queue given")
    else:
        with open("queue.txt", "w", encoding="utf-8") as file:
            file.write(queue.strip("```").replace("\\", "/"))
        await ctx.send("i tak the q, n eat it")



@client.hybrid_command()
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    await voice_client.disconnect()
    await ctx.send("bai bai")

@client.hybrid_command()
async def pause(ctx):
    voice_client = ctx.guild.voice_client
    voice_client.pause()
    await ctx.send("ok i wait")

@client.hybrid_command()
async def resume(ctx):
    voice_client = ctx.guild.voice_client
    voice_client.resume()
    await ctx.send("yay i playing again")
                               
# non music stuff

@client.hybrid_command(aliases=['sheep'])
async def shaun_the_sheep(ctx):
    await ctx.send("He’s Shaun the Sheep\nHe’s Shaun the Sheep\nHe even mucks about with those who cannot bleat\nKeep it in Mind,\nHe's One of a Kind\nOh life's a treat with Shaun the Sheep\nHe's Shaun the Sheep (He's Shaun the Sheep.)\nHe's Shaun the Sheep (He's Shaun the Sheep.)\nHe doesn't miss a trick or ever lose a beat (lose a beat.)\nPerhaps one day, you'll find a way to come and meet with Shaun the Sheep.\nOh, come and bleat with Shaun the Sheep! (Baaaaaaaaaaaaaaaaaaaaaaaaaa!)")

@client.hybrid_command()
async def shawn_the_sheep(ctx):
    await ctx.send("dont be pretentious and use shaun_the_sheep")

@client.hybrid_command()
async def baa(ctx, *, message=None):
    await ctx.message.delete()
    await ctx.send(message)

@client.event
async def on_message(message: discord.Message):
    await client.process_commands(message)
    if "!smortie" in message.content.lower():
        await asyncio.sleep(2)
        await message.channel.send("bru mik botol clon")
    elif message.content.startswith('!smort'):
        return
    elif message.author.id != 1186326404267266059 and message.author.id != 839794863591260182:
        if "baa" in message.content.lower():
            await message.channel.send("Baaaaaaaa!")
        if "help mi" in message.content.lower():
            await message.reply("PLS HELP MI TOO PLEASE")
        if "smortie" in message.content.lower() or "smartie" in message.content.lower() or "smorty" in message.content.lower() or "smort" in message.content.lower() or "smarty" in message.content.lower():
            await message.reply("omg me mention! i love smorties :D <:saveme:1334594782172811365><:saveme:1334594782172811365>")
        if "mik" in message.content.lower() or "milk" in message.content.lower() or "botol" in message.content.lower() or "🍼" in message.content.lower():
            await message.reply("mik 🍼")

@client.event
async def on_command_error(ctx, error):
    channel_id = 1131914463277240361
    channel = client.get_channel(channel_id)
    await channel.send(error)
    await channel.send(error.__traceback__)

keep_alive.keep_alive()
client.run(token)
