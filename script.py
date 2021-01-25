# import discord
from discord.ext import commands
from discord import utils, Intents, FFmpegOpusAudio
import os
import time
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


@bot.event
async def on_ready():
    print(f'logged in as {bot.user}.')


@bot.event
async def on_member_update(before, after):
    if before.name != 'Rich':  # TODO: or rl not in activities
        print(before.name)
        print('returning..')
        return

    # TODO: clean up these for loops
    for activity_0 in before.activities:
        if activity_0.name == 'Rocket League':
            break
    else:
        return

    for activity_1 in after.activities:
        if activity_1.name == 'Rocket League':
            break
    else:
        return

    print('activity state: ', activity_1.state)

    # # TODO: test - probably not needed now as we're testing for activity first
    # if not hasattr(activity_0, 'state'):
    #     return

    score_0 = activity_0.state.split()[1]
    score_1 = activity_1.state.split()[1]

    if is_now_losing(score_0, score_1):
        try:
            # TODO: get context here - make sure text channel and voice channel exist on the object else give default val
            ctx = await bot.get_context(before)
            await play_song(ctx)
            # messy, maybe get from user object?  TODO: replace guild and text_channel with ctx
            guild = bot.guilds[0]
            text_channel = guild.text_channels[0]
            await text_channel.send('let\'s gooo!')
        except CurrentlyPlayingError:
            print('inside CurrentlyPlayingError block for on_member_update')
        except Exception as e:
            print('something went wrong...')
            print(e)


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
        vc = utils.get(bot.voice_clients, guild=ctx.guild)
        if vc.is_playing():
            vc.stop()
            await ctx.send('Stopped playing music.')
        else:
            await ctx.send('Nothing to stop...')


@bot.command(name='test')
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command(name='yo', aliases=['summon', 'wag1'])
async def join_call(ctx):
    if not is_connected(ctx.guild):
        vc = ctx.guild.voice_channels[0]        # TODO: generalise this?
        await vc.connect()
        await ctx.send('Joined call.')
    else:
        await ctx.send('Already in call...')


@bot.command(name='bb', aliases=['fo', 'bye'])
async def leave_call(ctx):
    if is_connected(ctx.guild):
        vc = utils.get(bot.voice_clients, guild=ctx.guild)
        await vc.disconnect()
        await ctx.send('Left call.')
    else:
        # TODO: this is the case when bot is stopped via console and is still in disc call on startup
        await ctx.send('Not in call.')


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

    print('finished song')
    vc.stop()


def is_connected(guild):
    vc = utils.get(bot.voice_clients, guild=guild)
    return vc and vc.is_connected


bot.run(TOKEN)
