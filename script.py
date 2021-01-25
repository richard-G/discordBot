import discord
import os
import time
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.all()
client = discord.Client(intents=intents)


# TODO: move this to class dir?
class CurrentlyPlayingError(Exception):
    pass


@client.event
async def on_ready():
    print(f'logged in as {client.user}.')

    # guild = client.guilds[0]
    # vc1 = guild.voice_channels[0]

    # # await guild.change_voice_state(channel=vc1, self_mute=False, self_deaf=True)

    # vc = await vc1.connect()

    # audio_source = discord.FFmpegPCMAudio(
    #     executable="C:/dev/ffmpeg/bin/ffmpeg.exe", source="temp.mp3")
    # vc.play(audio_source)

    # # vc.start()
    # while vc.is_playing():
    #     # print('playing now..')
    #     time.sleep(1)
    # vc.stop()

    # await send_message()


@client.event
async def on_member_update(before, after):
    if before.name != 'Rich':  # TODO: or rl not in activities
        print(before.name)
        print('returning..')
        return

    for activity_0, activity_1 in zip(before.activities, after.activities):
        if activity_0.name == 'Rocket League':
            break

    print('activity state: ', activity_1.state)

    score_0 = activity_0.state.split()[1]
    score_1 = activity_1.state.split()[1]

    if is_now_losing(score_0, score_1):
        try:
            await play_song()
            # messy, maybe get from user object?
            guild = client.guilds[0]
            text_channel = guild.text_channels[0]
            await text_channel.send('let\'s gooo!')
        except CurrentlyPlayingError:
            print('inside CurrentlyPlayingError block for on_member_update')
        except Exception as e:
            print('something went wrong...')
            print(e)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hype'):
        try:
            await play_song()
            # await message.channel.send('yessir')   # TODO: make this fire as play_song() starts
        except CurrentlyPlayingError:
            print('inside CurrentlyPlayingError block for on_message')
            await message.channel.send('open your ears mate, playing it right now!')
        # await play_song()


def is_now_losing(score0, score1):
    # case where score is unchanged
    if score0 == score1:
        return False

    # case where initial scoreline wasn't even
    if score0.split(':')[0] != score0.split(':')[1]:
        return False

    # case where we are now winning
    if int(score1.split(':')[0]) > int(score1.split(':')[1]):
        print('we scored!')
        return False

    return True

# TODO: make this a command? or make a command invoke this function


async def play_song():
    print('H Y P E')

    # TODO: generalise this, maybe pass in as arg from parent
    guild = client.guilds[0]
    vc1 = guild.voice_channels[0]
    text_channel = guild.text_channels[0]

    # TODO: check if already playing song, if so then don't play

    if not is_connected(guild):
        print('connecting to voice channel..')
        vc = await vc1.connect()
    else:
        vc = discord.utils.get(client.voice_clients, guild=guild)
        print('already connected to channel')

    # TODO: message this in the chat, maybe throw and catch it in parent?
    if vc.is_playing():
        raise CurrentlyPlayingError()
        # await text_channel.send('open your ears mate, playing it right now!')
        # print('open your ears mate, playing it right now!')
        # return

    audio_source = discord.FFmpegOpusAudio(
        executable="C:/dev/ffmpeg/bin/ffmpeg.exe", source="songs/la-vida-loca.mp3")   # TODO: check this new path works
    vc.play(audio_source)

    # TODO: ensure this only plays if song was triggered from a message command
    # await text_channel.send('let\'s gooooo!')

    # vc.start()
    seconds = 0
    while vc.is_playing():
        seconds += 1
        print('playing now.. ', seconds)
        await asyncio.sleep(1)

    print('finished song')
    vc.stop()


def is_connected(guild):
    vc = discord.utils.get(client.voice_clients, guild=guild)
    return vc and vc.is_connected


client.run(TOKEN)
