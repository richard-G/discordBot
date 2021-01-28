# import discord
from discord.ext import commands
from discord import utils, Intents, FFmpegOpusAudio
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
intents = Intents.all()
bot = commands.Bot(intents=intents, command_prefix='$')


# TODO: make dictionary of commands to return
# eg. "NotInCall", "NotInVoiceChannel"
responses = {
    not_in_call: 'You must be in a call to use this command.',
    different_voice_channel: 'You must be in the same voice channel as me to use this command.'
}

# TODO: move this to class dir?


class CurrentlyPlayingError(Exception):
    pass


class WrongVoiceChannel(Exception):
    pass


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
        return

    if not is_playing_rl(before, after):
        return

    if not is_now_losing(before, after):
        return

    try:
        if not before.voice:
            return
        else:
            v_channel = before.voice.channel
            # TODO: don't try to join voice channel if already in
            vc = await v_channel.connect()
        await play_song(vc)
    except CurrentlyPlayingError:
        print('inside CurrentlyPlayingError exception')
    except Exception as e:
        print('something went wrong... ', e)


# TODO: if music is paused then resume
@bot.command(name='play')
async def play(ctx):
    # check that member making command is in a voice channel
    member = ctx.author
    if member.voice:
        |
        v_channel = member.voice.channel
        # check if bot has an active voice client in the guild
        if utils.get(bot.voice_clients, guild=ctx.guild):
            # check if bot is in same voice channel as the caller
            if not utils.get(bot.voice_clients, channel=v_channel):
                await ctx.send(responses.different_voice_channel)
                return
            else:
                vc = utils.get(bot.voice_clients, channel=v_channel)
        else:
            # await ctx.send('I\'m not in a voice channel, type `$join` to get me in one.')
            vc = await v_channel.connect()

    else:
        await ctx.send(responses.not_in_call)
        return

    try:
        await play_song(vc)
    except CurrentlyPlayingError:
        # probably add song to queue here in future
        await ctx.send('Already playing music.')
        return


@bot.command(name='stop')
async def stop(ctx):

    # check that member making command is in a voice channel
    member = ctx.author
    if member.voice:
        v_channel = member.voice.channel
        # check if bot has an active voice client in the guild
        if utils.get(bot.voice_clients, guild=ctx.guild):
            # check if bot is in same voice channel as the caller
            if not utils.get(bot.voice_clients, channel=v_channel):
                await ctx.send(responses.different_voice_channel)
                return
        else:
            await ctx.send('I\'m not in a voice channel, type `$join` to get me in one.')
            return
    else:
        await ctx.send(responses.different_voice_channel)
        return

    vc = utils.get(bot.voice_clients, channel=v_channel)

    if vc.is_playing() or vc.is_paused():
        vc.stop()
        await ctx.send('Stopped playing music.')
    else:
        await ctx.send('Nothing to stop...')

# TODO: test
@bot.command(name='join', aliases=['yo', 'summon', 'wag1'])
async def join_call(ctx):
    member = ctx.author
    if not member.voice:
        await ctx.send(responses.not_in_call)
        return

    v_channel = member.voice.channel

    if utils.get(bot.voice_clients, channel=v_channel):
        # case where bot is already in same voice call as caller
        await ctx.send('Already in call.')
        return
    elif utils.get(bot.voice_clients, guild=ctx.guild):
        # case where bot is in another call on the server
        # TODO: decide what to do here, either refuse command or leave curr voice channel to join new one
        await ctx.send('Already in another call.')
        return

    await v_channel.connect()
    await ctx.send('Joined call.')


@bot.command(name='leave', aliases=['bb', 'fo', 'bye'])
async def leave_call(ctx):
    # TODO: fix this
    if not ctx.author.voice:
        await ctx.send(responses.not_in_call)

    if is_connected(ctx.author.voice.channel):
        vc = utils.get(bot.voice_clients, guild=ctx.guild)
        await vc.disconnect()
        await ctx.send('Left call.')
    else:
        # TODO: this is the case when bot is stopped via console and is still in disc call on startup
        await ctx.send('Not in call.')


# TODO
@bot.command(name='pause')
async def pause(ctx):
    # TODO: check caller is in same voice call as the bot
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
    # TODO: check caller is in same voice call as the bot
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

    # case where rocket league rich presence isn't in state
    if not len(rl_0.state.split()) == 3:
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
        return False

    return True


def is_playing_rl(before, after):
    # TODO: check here or to check rl state is using rich presence
    return any(activity.name == 'Rocket League' for activity in before.activities) and any(activity.name == 'Rocket League' for activity in after.activities)


async def play_song(vc):
    # takes as argument the voice client to play music to
    print('H Y P E')

    if not vc:
        print('shouldn\'t get here...')
        print('play_song called without a voice client')
        return

    if vc.is_playing():
        raise CurrentlyPlayingError()

    audio_source = FFmpegOpusAudio(
        executable="C:/dev/ffmpeg/bin/ffmpeg.exe", source="songs/la-vida-loca.mp3")

    vc.play(audio_source)

    seconds = 0
    while vc.is_playing():
        seconds += 1
        print('playing now.. ', seconds)
        await asyncio.sleep(1)


def is_connected(v_channel):
    vc = utils.get(bot.voice_clients, channel=v_channel)

    return vc and vc.is_connected


bot.run(TOKEN)
