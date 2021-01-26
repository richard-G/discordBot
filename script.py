# import discord
from discord.ext import commands
from discord import utils, Intents, FFmpegOpusAudio
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
intents = Intents.all()
# TODO: check this still works with on_member_update in getting rich text
bot = commands.Bot(intents=intents, command_prefix='$')


# TODO: move this to class dir?
class CurrentlyPlayingError(Exception):
    pass


# TODO
class track():
    def __init__(self, name, artist, path, source):
        self.name = name
        self.artist = artist
        self.path = path
        self.source = source

    def __str__(self):
        return f'{self.artist} - {self.name}'

    def convert(self):
        if self.source == 'local':
            return FFmpegOpusAudio(source=self.path, executable='C:/dev/ffmpeg/bin/ffmpeg.exe')

        # TODO
        if self.source == 'youtube':
            pass


@bot.event
async def on_ready():
    print(f'logged in as {bot.user}.')


@bot.event
async def on_member_update(before, after):
    if before.name == bot.user:
        # TODO: test if this condition is ever met
        print('on_member_update called on bot')
        return

    # unused
    # if before.name != 'Rich':  # TODO: or rl not in activities
    #     print(before.name)
    #     print('returning..')
    #     return

    # TODO: test
    if not is_playing_rl(before, after):
        return

    # TODO: test
    if not is_now_losing(before, after):
        return

    try:
        ctx = await bot.get_context(before)
        await play_song(ctx)
    except CurrentlyPlayingError:
        print('inside CurrentlyPlayingError exception')
    except Exception as e:
        print('something went wrong... ', e)

    # # TODO: remove after testing
    # for activity_0 in before.activities:
    #     if activity_0.name == 'Rocket League':
    #         break
    # else:
    #     return

    # for activity_1 in after.activities:
    #     if activity_1.name == 'Rocket League':
    #         break
    # else:
    #     return

    # print('activity state: ', activity_1.state)

    # # TODO: test - probably not needed now as we're testing for activity first
    # if not hasattr(activity_0, 'state'):
    #     return

    # score_0 = activity_0.state.split()[1]
    # score_1 = activity_1.state.split()[1]

    # if is_now_losing(score_0, score_1):
    #     try:
    #         # TODO: get context here - make sure text channel and voice channel exist on the object else give default val
    #         ctx = await bot.get_context(before)
    #         await play_song(ctx)
    #         # messy, maybe get from user object?  TODO: replace guild and text_channel with ctx
    #         guild = bot.guilds[0]
    #         text_channel = guild.text_channels[0]
    #         await text_channel.send('let\'s gooo!')
    #     except CurrentlyPlayingError:
    #         print('inside CurrentlyPlayingError block for on_member_update')
    #     except Exception as e:
    #         print('something went wrong...')
    #         print(e)


# TODO: if music is paused then resume
@bot.command(name='play')
async def play(ctx):
    try:
        await play_song(ctx)
    except CurrentlyPlayingError:
        # will probably add it to queue
        await ctx.send('Already playing music...')


@bot.command(name='stop')
async def stop(ctx):
    if is_connected(ctx.guild):
        vc = ctx.voice_client
        if vc.is_playing() or vc.is_paused():
            vc.stop()
            await ctx.send('Stopped playing music.')
        else:
            await ctx.send('Nothing to stop...')


# # TODO
# @bot.command(name='help')
# async def test(ctx):
#     pass


@bot.command(name='join', aliases=['yo', 'summon', 'wag1'])
async def join_call(ctx):
    if not is_connected(ctx.guild):
        vc = ctx.guild.voice_channels[0]        # TODO: generalise this?
        await vc.connect()
        await ctx.send('Joined call.')
    else:
        await ctx.send('Already in call...')


@bot.command(name='leave', aliases=['bb', 'fo', 'bye'])
async def leave_call(ctx):
    if is_connected(ctx.guild):
        vc = utils.get(bot.voice_clients, guild=ctx.guild)
        await vc.disconnect()
        await ctx.send('Left call.')
    else:
        # TODO: this is the case when bot is stopped via console and is still in disc call on startup
        await ctx.send('Not in call.')


# TODO
@bot.command(name='pause')
async def pause(ctx):
    if ctx.voice_client:
        vc = ctx.voice_client
        if vc.is_playing():
            vc.pause()
            await ctx.send('Paused music.')
        elif vc.is_paused():
            await ctx.send('Music is already paused.')
        else:
            await ctx.send('No music to pause.')
    else:
        print('NOT ctx.voice_client')


# TODO
@bot.command(name='resume')
async def resume(ctx):
    if ctx.voice_client:
        vc = ctx.voice_client
        if vc.is_paused():
            vc.resume()
            await ctx.send('Resuming music.')
        elif vc.is_playing():
            await ctx.send('Music is currently playing.')
        else:
            await ctx.send('No music to resume.')
    else:
        print('NOT ctx.voice_client')


def is_now_losing(before, after):
    # extract rl activities from member objects
    rl_0 = next(
        (activity for activity in before.activities if activity.name == 'Rocket League'), None)
    rl_1 = next(
        (activity for activity in after.activities if activity.name == 'Rocket League'), None)

    if not rl_0 and rl_1:
        print('this condition should never be met (not rl_0 and rl_1)')
        return False

    # extract scores from rl activities
    score_0 = rl_0.state.split()[1]
    score_1 = rl_1.state.split()[1]

    # case where score is unchanged
    if score_0 == score_1:
        return False

    # case where initial scoreline wasn't even
    if score_0.split(':')[0] != score_0.split(':')[1]:
        return False

    # case where we are now winning
    if int(score_1.split(':')[0]) > int(score_1.split(':')[1]):
        print('we scored!')
        return False

    return True


def is_playing_rl(before, after):
    return any(activity.name == 'Rocket League' for activity in before.activities) and any(activity.name == 'Rocket League' for activity in after.activities)


async def play_song(ctx):
    print('H Y P E')

    # TODO: generalise this, pass in as ctx arg from parent
    guild = ctx.guild
    vc1 = guild.voice_channels[0]
    text_channel = guild.text_channels[0]

    if not is_connected(guild):
        print('connecting to voice channel..')
        vc = await vc1.connect()
    else:
        vc = utils.get(bot.voice_clients, guild=guild)
        print('already connected to channel')

    if vc.is_playing():
        raise CurrentlyPlayingError()

    audio_source = FFmpegOpusAudio(
        executable="C:/dev/ffmpeg/bin/ffmpeg.exe", source="songs/la-vida-loca.mp3")

    vc.play(audio_source)

    # TODO: check this works if invoked from on_member_update evt, probably won't because no channel is given
    if ctx.message.channel:
        await ctx.send('Playing now. :fire:')
    else:
        # should only get in here if song is auto played (via rocket league score)
        print('ctx.message.channel did not exist.')

    seconds = 0
    while vc.is_playing():
        seconds += 1
        print('playing now.. ', seconds)
        await asyncio.sleep(1)

    # print('finished song')
    # vc.stop()   # TODO: test


def is_connected(guild):
    vc = utils.get(bot.voice_clients, guild=guild)
    return vc and vc.is_connected


bot.run(TOKEN)
