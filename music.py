# region setup
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
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from dyslexicloglog import Autocorrector

intents = discord.Intents.all()
intents.members = True

load_dotenv()

bot_prefix = "smort"
codespace = "docker"

if os.getenv("WORKSPACE") == "actions":
    codespace = os.getenv('WORKSPACE')

if bot_prefix == "smort" and codespace != "docker":
    token = os.getenv("SMORT_TOKEN")
else:
    token = os.getenv("ROBO_TOKEN")

client = commands.Bot(
    command_prefix=[f"!{bot_prefix} ", f"!{bot_prefix} "],
    intents=intents)

ac = Autocorrector()


@client.event
async def on_ready():
    print('Roboduck is ready')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="ITS SHAUN THE SHEEP!"))
    await client.tree.sync()
# endregion


# region helper functions
async def view_queue_file():
    with open("queue.txt", encoding="utf-8") as queue_file:
        msg = ""
        for row in queue_file:
            if row != "\n":
                msg += row
        return msg

async def write_to_queue_file(ctx, mode, queue):
    if queue == None:
        await ctx.send("no queue given")
    else:
        await edit_queue_file(mode, queue)
        await ctx.send("i tak the q, n eat it")

async def edit_queue_file(mode, queue):
    if mode == "append":
        with open("queue.txt", "a+", encoding="utf-8") as file:
            file.seek(0)
            current_file = file.read().strip()
            if current_file != "":
                file.write("\n" + queue.strip("```").replace("\\", "/").replace(".mp3 ", ".mp3\n").replace(".m4a ", ".m4a\n"))
            else:
                file.write(queue.strip("```").replace("\\", "/").replace(".mp3 ", ".mp3\n").replace(".m4a ", ".m4a\n"))
    elif mode == "overwrite":
        with open("queue.txt", "w", encoding="utf-8") as file:
            file.write(queue.strip("```").replace("\\", "/").replace(".mp3 ", ".mp3\n").replace(".m4a ", ".m4a\n"))


async def autocorrector(query:str, number:int=1, separator:str=" "):
    input_list = query.split(separator)
    if number not in [1,2,3]:
        return "please choose a number between 1 to 3 inclusive"
    
    ac_results = ac.top3(input_list)

    if number == 3:
        return ac_results
    else:
        for key in ac_results:
            for i in range(3-number):
                ac_results[key].pop(-1)
        return ac_results

async def prettify_autocorrector(query:str, number:int=1, separator:str=" "):
    ac_results = await autocorrector(query, number, separator)
    msg = ""
    for key in ac_results:
        output = []
        word_list = ac_results[key.lower()]

        for i in range(1, len(word_list)+1):
            output.append(f"{i}. {word_list[i-1]}")
        msg += f'`{key}`: {" ".join(output)}\n'
    return msg



async def search_songs(filter:str="title", query:str="None"):
    all_songs = ""
    songs = []
    distinct_songs = []
    query = query.strip("```").replace("\\", "/")
    for path, subdirs, files in os.walk(f"playlists"):
        for name in files:
            if ".git" not in path and name not in distinct_songs:
                distinct_songs.append(name)
                all_songs += f'{os.path.join(path, name)}?'.removeprefix(f"playlists").replace("\\", "/")
    all_songs = all_songs.split("?")
    all_songs.pop(-1)

    song_dicts = [{"title": music_tag.load_file(f"playlists/{song}")['title'], "artist": music_tag.load_file(f"playlists/{song}")['artist'], "album": music_tag.load_file(f"playlists/{song}")['album'], "file_path": song} for song in all_songs]

    if filter == "title":
        songs = [song['file_path'] for song in song_dicts if query.lower() in str(song['title']).lower() or query.lower() in str(song['file_path']).lower()]
    elif filter == "artist":
        songs = [song['file_path'] for song in song_dicts if query.lower() in str(song['artist']).lower()]
    elif filter == "album":
        songs = [song['file_path'] for song in song_dicts if query.lower() in str(song['album']).lower()]
    elif filter == "title_artist":
        try:
            query_list = query.split(",")
            title = query_list[0]
            artist = query_list[1]
            songs = [song['file_path'] for song in song_dicts if (title.lower() in str(song['title']).lower() or title.lower() in str(song['file_path']).lower()) and artist.lower() in str(song['artist']).lower()]
        except IndexError:
            songs = [song['file_path'] for song in song_dicts if query.lower() in str(song['title']).lower() or query.lower() in str(song['file_path']).lower()]

    return(songs)


async def get_track_duration(file, full_file_path):
    if file.endswith(".mp3"):
        time = MP3(full_file_path).info.length + 3
    else:
        time = MP4(full_file_path).info.length + 3
    return(time)


async def sleep_until_song_ends(ctx):
    voice_client = ctx.guild.voice_client
    while voice_client.is_playing() or voice_client.is_paused():
        await asyncio.sleep(1)



async def ac_search_songs(ctx, filter:str="title", query:str="None"):
    songs = await search_songs(filter, query)

    if songs == []:
        ac_query = await autocorrector(query, 1)
        ac_word = ac_query[query][0]
        await ctx.send(f"perhaps you meant {ac_word}?")
        songs = await search_songs(filter, ac_word)
    
    return songs

async def send_codeblock(ctx, msg, *, view=None):
    if len(msg) > 1993:
        if len(msg) > 3993:
            first_msg = msg[:1993]
            second_msg = msg[1993:3987]
            third_msg = msg[3987:].strip()
            await ctx.send(f"```{first_msg}```")
            await ctx.send(f"```{second_msg}```")
            await ctx.send(f"```{third_msg}```")
        else:
            first_msg = msg[:1993]
            second_msg = msg[1993:].strip()
            await ctx.send(f"```{first_msg}```")
            await ctx.send(f"```{second_msg}```")
    else:
        await ctx.send(f"```{msg}```", view=view)
# endregion


# music stuffs

playlist_choices = [app_commands.Choice(name="continue", value="continue"), app_commands.Choice(name="master", value="master"), app_commands.Choice(name="local", value="local")]
for playlist in os.listdir(f"playlists"):
    if "." not in playlist:
        playlist_choices.append(app_commands.Choice(name=playlist, value=playlist))

@client.hybrid_command(description="plays a playlist given a vc id and playlist name", brief="plays a playlist")
@app_commands.describe(playlist="wat i play, continue if imported queue, master if all songs in all playlists", shuffle="say shuffle if yes", loop="say loop if yes")
@app_commands.choices(playlist=playlist_choices, shuffle=[
    app_commands.Choice(name='shuffle', value="shuffle"),
    app_commands.Choice(name='no', value="no")
], loop=[
    app_commands.Choice(name='loop', value="loop"),
    app_commands.Choice(name='no', value="no")
])
async def play(ctx, channel: discord.VoiceChannel, playlist=None, shuffle=None, loop="no"):

    folder_path = f"playlists/{playlist}"
    loop_playlist = False

    # region check if playlist exists
    if playlist == "master":
        await ctx.send("ok playing all songs")
        folder_path = f"playlists"
    elif playlist == "continue":
        await ctx.send("ok i continue")
        folder_path = f"playlists"
    elif playlist == None:
        await ctx.send("no playlist? ok i play queue")
        folder_path = f"playlists/queue"
        playlist = "queue"

    elif os.path.isdir(folder_path) == False:
        await ctx.send("umm i cant find the playlist :( (i play queue)")
        folder_path = f"playlists/queue"
        playlist = "queue"

    else:
        await ctx.send(f"found ur playlist yay!!! playing {playlist}")
        folder_path = f"playlists/{playlist}"
    # endregion

    music_files = os.listdir(folder_path)

    # region special playlists
    # master: add all songs to music_files
    if playlist == "master":
        music_files = ""
        for path, subdirs, files in os.walk(folder_path):
            subdirs[:] = [d for d in subdirs if d != ".git" and d != "burnouttour"]
            for name in files:
                if not name in music_files:
                    music_files += f'{os.path.join(path, name)}?'.removeprefix(folder_path)
        music_files = music_files.split("?")
        music_files.pop(-1)

    # continue: get queue from queue.txt
    elif playlist == "continue":
        with open("queue.txt", encoding="utf-8") as file:
            music_files = file.readlines()
            music_files = [song.strip() for song in music_files]
    # endregion


    # region check if shuffle/loop is enabled
    if shuffle == None:
        await ctx.send("no shuffle mode, i go alphabetical")
    elif shuffle.lower() == "shuffle":
        await ctx.send("shuffle mode go brr")
        random.shuffle(music_files)

    if loop.lower() == "loop":
        await ctx.send("ok i loop")
        loop_playlist = True
    # endregion


    # region write songs to queue
    # write all songs to queue.txt
    dupe_music_files = music_files.copy()

    if playlist == "master":
        with open("queue.txt", "w", encoding="utf-8") as file:
            for music in dupe_music_files:
                music.strip()
                if music == "\n" or music == "":
                    dupe_music_files.remove(music)
            file.write("\n".join(dupe_music_files))

    # write songs in playlist to queue.txt
    elif playlist != "continue":
        with open("queue.txt", "w", encoding="utf-8") as file:
            music_files_with_playlist_path = [f"/{playlist}/{song}" for song in dupe_music_files]
        
            file.write("\n".join(music_files_with_playlist_path))
    # endregion


    # get channel
    channel_id = channel.id
    channel = client.get_channel(channel_id)


    # actual playing code
    voice_client = await channel.connect()
    dupe_music_files_2 = music_files.copy()

    for i in range(len(music_files)):
        music_files = [file.replace("\\", '/') for file in music_files]


    # region loading playing variables
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
    # endregion


        f = music_tag.load_file(file_to_load)
        time = await get_track_duration(music_files[i], full_file_path)


    # region buttons
        class QueueButtons(discord.ui.View):
            @discord.ui.button(label='delete', style=discord.ButtonStyle.red)
            async def deletequeue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
                await interaction.response.edit_message(content="queue go bai bai", view=None)

        class Buttons(discord.ui.View):
            @discord.ui.button(label='pause', style=discord.ButtonStyle.blurple)
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
                msg = await view_queue_file()
                await interaction.response.send_message(f"```{msg[:1993]}```", view=QueueButtons(timeout=None))
            @discord.ui.button(label='stop', style=discord.ButtonStyle.red)
            async def stop(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
                await voice_client.disconnect()
                await interaction.response.edit_message(content='bai bai', view=None)
    # endregion

        voice_client.play(discord.FFmpegPCMAudio(file_to_play))
        await ctx.send(f"playing {f['title']} - {f['artist']}", silent=True, view=Buttons(timeout=None))
        if i < len(music_files)-1:
            popped = queue_list.pop(0)
            if loop_playlist:
                queue_list.append(popped)
        with open("queue.txt", "w", encoding="utf-8") as file:
            file.write("\n".join(queue_list))

        task = asyncio.create_task(sleep_until_song_ends(ctx))
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
async def play24(ctx, *, channel: discord.VoiceChannel=None, file="sheep.mp3"):
    channel_id = 1132046013360779434
    if channel != None:
        channel_id = channel.id
    folder_path = f"playlists"
    song = await ac_search_songs(ctx, "title", file)
    file_path = f"{folder_path}/{song[0]}"

    time = await get_track_duration(song[0], file_path)

    channel = client.get_channel(channel_id)

    voice_client = await channel.connect()
    await ctx.send(f"playing {song[0]} 24/7. please disconnect me from the voice channel if you want to play something else :D")

    while True:
        voice_client.play(discord.FFmpegPCMAudio(file_path))
        await asyncio.sleep(time)
        voice_client.stop()



@client.hybrid_command(description="plays a file once")
async def playfile(ctx, channel: discord.VoiceChannel, *, file=None):
    channel_id = channel.id
    folder_path = f"playlists"
    song = await ac_search_songs(ctx, "title_artist", file)
    file_path = f"{folder_path}/{song[0]}"
    f = music_tag.load_file(file_path)

    # region buttons
    class Buttons(discord.ui.View):
        @discord.ui.button(label='pause', style=discord.ButtonStyle.blurple)
        async def pause(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            voice_client.pause()
            await interaction.response.send_message('ok i wait')
        @discord.ui.button(label='resume', style=discord.ButtonStyle.success)
        async def resume(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            voice_client.resume()
            await interaction.response.send_message('yay i sing')
        @discord.ui.button(label='stop', style=discord.ButtonStyle.red)
        async def stop(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await voice_client.disconnect()
            await interaction.response.edit_message(content='bai bai', view=None)
    # endregion

    channel = client.get_channel(channel_id)

    voice_client = await channel.connect()
    await ctx.send(f"playing {f['title']} :D ill disconnect when its done", view=Buttons(timeout=None))

    voice_client.play(discord.FFmpegPCMAudio(file_path))
    await sleep_until_song_ends(ctx)
    await voice_client.disconnect()
    await ctx.send("bai bai")



@client.hybrid_command()
@app_commands.choices(save_only=[
    app_commands.Choice(name='true', value="true"),
    app_commands.Choice(name='false', value="false")
])
async def playlocalfile(ctx, channel: discord.VoiceChannel, file: discord.Attachment, save_only: str = "false"):
    await ctx.defer()

    channel_id = channel.id
    folder_path = f"playlists/local"
    file_path = f"{folder_path}/{file.filename}"
    if not os.path.exists("playlists/local"):
        os.makedirs("playlists/local")
    await file.save(file_path)

    # region buttons
    class Buttons(discord.ui.View):
        @discord.ui.button(label='pause', style=discord.ButtonStyle.blurple)
        async def pause(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            voice_client.pause()
            await interaction.response.send_message('ok i wait')
        @discord.ui.button(label='resume', style=discord.ButtonStyle.success)
        async def resume(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            voice_client.resume()
            await interaction.response.send_message('yay i sing')
        @discord.ui.button(label='stop', style=discord.ButtonStyle.red)
        async def stop(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await voice_client.disconnect()
            await interaction.response.edit_message(content='bai bai', view=None)
    # endregion

    if save_only != "true":
        channel = client.get_channel(channel_id)

        voice_client = await channel.connect()
        await ctx.send(f"playing {file.filename} :D ill disconnect when its done", view=Buttons(timeout=None))

        voice_client.play(discord.FFmpegPCMAudio(file_path))
        await sleep_until_song_ends(ctx)
        await voice_client.disconnect()
        await ctx.send("bai bai")



@client.hybrid_command(description="imports all songs of the artist")
async def playartist(ctx, artist=None):

    songs = await ac_search_songs(ctx, "artist", artist)
    queue = "\n".join(songs)
    await send_codeblock(ctx, queue)
    await write_to_queue_file(ctx, "overwrite", queue)



@client.hybrid_command(description="imports all songs of an album")
async def playalbum(ctx, album=None):

    songs = await ac_search_songs(ctx, "album", album)
    queue = "\n".join(songs)
    await send_codeblock(ctx, queue)
    await write_to_queue_file(ctx, "overwrite", queue)



@client.hybrid_command(description="imports songs from spotify playlist")
@app_commands.describe(url="wat link i import", importmode="overwrite the queue or append")
@app_commands.choices(mode=[
    app_commands.Choice(name='playlist', value="playlist"),
    app_commands.Choice(name='track', value="track")
], importmode=[
    app_commands.Choice(name='overwrite', value="overwrite"),
    app_commands.Choice(name='append', value="append")
])
async def playspotify(ctx, mode="playlist", url=None, importmode="overwrite"):

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    await ctx.defer()
    queue_list = []
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

    if mode == "playlist":
        results = sp.playlist_tracks(url, limit=100)
        tracks = results['items']
        while results['next']:
            results = sp.next(tracks)
            tracks.extend(results['items'])

    else:
        results = sp.track(url)
        tracks = [results]

    for song in tracks:
        if mode == "playlist":
            track_name = song['track']['name']
        else:
            track_name = song['name']
        search_result = await search_songs("title", track_name)
        try:
            queue_list.append(search_result[0])
        except IndexError:
            continue
            
    queue = "\n".join(queue_list)
    
    class QueueButtons(discord.ui.View):
        @discord.ui.button(label='delete', style=discord.ButtonStyle.red)
        async def deletequeue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.edit_message(content="queue go bai bai", view=None)
        @discord.ui.button(label='import', style=discord.ButtonStyle.secondary)
        async def importqueue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await edit_queue_file("overwrite", interaction.message.content)
            await interaction.response.send_message("i tak the q, n eat it")
        @discord.ui.button(label='append', style=discord.ButtonStyle.secondary)
        async def appendqueue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await edit_queue_file("append", interaction.message.content)
            await interaction.response.send_message("i tak the q, n eat it")
            
    await send_codeblock(ctx, queue, view=QueueButtons(timeout=None))
    await write_to_queue_file(ctx, importmode, queue)



@client.hybrid_command(description="imports a song from a youtube link")
@app_commands.describe(url="wat link i import")
async def playyoutube(ctx, url=None):
    if codespace != "actions":
        await ctx.defer()
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'outtmpl': 'playlists/local/%(title)s.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace("\\", "/").replace("playlists", "")
        await ctx.send(f"saved it as `{filename}`, pls use `/playfile` to play it")
    else:
        await ctx.send("only ysis can")



@client.hybrid_command(description="imports all jp songs")
async def playjp(ctx):

    artists = [
        "YOASOBI", "Rokudenashi", "tuki", "ヨルシカ"
    ]

    for i in range(0, len(artists)-1):
        songs = await ac_search_songs(ctx, "artist", artists[i])
        queue = "\n".join(songs)
        if i != 0:
            await edit_queue_file("append", queue)
        else:
            await edit_queue_file("overwrite", queue)

    msg = await view_queue_file() 
    await send_codeblock(ctx, msg)



@client.hybrid_command(aliases=['playlist'])
@app_commands.describe(playlist="wat u si")
async def playlists(ctx, *, playlist=None):

    if playlist == None:
        playlists = os.listdir(f"playlists")
        try:
            playlists.remove(".git")
        except:
            pass
        playlists = '\n'.join(playlists)
        await ctx.send(f"playlists:\n{playlists}\n\nuse !smort play <playlist> to play a playlist, or !smort playlists <playlist> to list the songs in a playlist")
  
    else:
        songs = os.listdir(f"playlists/{playlist}")
        new_songs: str = ""
        for song in songs:
            f = music_tag.load_file(f"playlists/{playlist}/{song}")
            new_songs += f"{f['title']} - {str(f['artist']).split(',')[0]} ({song.split('.')[1]})\n"
            msg = f"songs in {playlist}:\n{new_songs}"
        await send_codeblock(ctx, msg)



@client.hybrid_command()
@app_commands.choices(filter=[
    app_commands.Choice(name='title', value="title"),
    app_commands.Choice(name='artist', value="artist"),
    app_commands.Choice(name='album', value='album'),
    app_commands.Choice(name='title + artist', value="title_artist")
])
async def search(ctx, filter="title", query=None):
    class QueueButtons(discord.ui.View):
        @discord.ui.button(label='delete', style=discord.ButtonStyle.red)
        async def deletequeue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.edit_message(content="queue go bai bai", view=None)
        @discord.ui.button(label='import', style=discord.ButtonStyle.secondary)
        async def importqueue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await edit_queue_file("overwrite", interaction.message.content)
            await interaction.response.send_message("i tak the q, n eat it")
        @discord.ui.button(label='append', style=discord.ButtonStyle.secondary)
        async def appendqueue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await edit_queue_file("append", interaction.message.content)
            await interaction.response.send_message("i tak the q, n eat it")

    songs = await ac_search_songs(ctx, filter, query)

    msg = "\n".join(songs)
    await send_codeblock(ctx, msg, view=QueueButtons(timeout=None))



@client.hybrid_command(aliases=['q'])
async def queue(ctx):
    class QueueButtons(discord.ui.View):
        @discord.ui.button(label='delete', style=discord.ButtonStyle.red)
        async def deletequeue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await interaction.response.edit_message(content="queue go bai bai", view=None)
        @discord.ui.button(label='import', style=discord.ButtonStyle.secondary)
        async def importqueue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await edit_queue_file("overwrite", interaction.message.content)
            await interaction.response.send_message("i tak the q, n eat it")
        @discord.ui.button(label='append', style=discord.ButtonStyle.secondary)
        async def appendqueue(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            await edit_queue_file("append", interaction.message.content)
            await interaction.response.send_message("i tak the q, n eat it")

    msg = await view_queue_file()
    await send_codeblock(ctx, msg, view=QueueButtons(timeout=None))



@client.hybrid_command(aliases=['import'])
@app_commands.describe(queue="wat i nom")
async def importqueue(ctx, *, queue:str=None):
    await write_to_queue_file(ctx, "overwrite", queue)


@client.hybrid_command(aliases=['append'])
@app_commands.describe(queue="wat i nom")
async def appendqueue(ctx, *, queue:str=None):
    await write_to_queue_file(ctx, "append", queue)


@client.hybrid_command()
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    await voice_client.disconnect()
    await ctx.send("bai bai")

@client.hybrid_command()
async def pause(ctx):
    voice_client = ctx.guild.voice_client
    await voice_client.pause()
    await ctx.send("ok i wait")

@client.hybrid_command()
async def resume(ctx):
    voice_client = ctx.guild.voice_client
    await voice_client.resume()
    await ctx.send("ok i sing")

# region non music stuff
@client.hybrid_command(aliases=['ac'])
@app_commands.describe(number="an integer from 1-3 inclusive, displays top n results")
async def autocorrect(ctx, query:str="None", *, number:str="1"):
    msg = await prettify_autocorrector(query, int(number))
    await ctx.send(msg)


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

bot_id_list = [1186326404267266059, 839794863591260182, 944245571714170930, 1396935480284680334]

@client.event
async def on_message(message: discord.Message):
    await client.process_commands(message)
    if codespace == "actions":
        if "!smortie" in message.content.lower():
            await asyncio.sleep(2)
            await message.channel.send("bru mik botol clon")
        elif message.content.startswith('!smort'):
            return
        elif message.author.id not in bot_id_list:
            if "baa" in message.content.lower():
                await message.channel.send("Baaaaaaaa!")
            if "help mi" in message.content.lower():
                await message.reply("PLS HELP MI TOO PLEASE")
            if "smortie" in message.content.lower() or "smartie" in message.content.lower() or "smorty" in message.content.lower() or "smort" in message.content.lower() or "smarty" in message.content.lower():
                await message.reply("omg me mention! i love smorties :D <:saveme:1334594782172811365><:saveme:1334594782172811365>")
            if "mik" in message.content.lower() or "milk" in message.content.lower() or "botol" in message.content.lower() or "🍼" in message.content.lower():
                await message.reply("mik 🍼")
            if " hat" in message.content.lower():
                await message.channel.send("""🎩 
.    .
v""")

@client.event
async def on_command_error(ctx, error):
    channel_id = 1131914463277240361
    channel = client.get_channel(channel_id)
    await channel.send(error)
    await channel.send(error.__traceback__)
# endregion

keep_alive.keep_alive()
client.run(token)
