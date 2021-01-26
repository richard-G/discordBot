# Discord Music Bot

This is a bot developed for discord with various functionalities largely relating to music.

## Dependencies

- Python 3.0 or greater running in a development environment (such as [Anaconda](https://www.anaconda.com/products/individual))
- Various Python module imports as shown in the top of `script.py`.
- [FFMPegAudio](https://ffmpeg.org/download.html). This is used to convert tracks into an audio source that the discord modules can play.

## Setup

A new discord application must first be created in the Discord Developer Portal in order to retrieve an API token. This must be placed in a `.env` file as shown in `.env.example`.

This can be done [here](https://discord.com/developers/applications).

After following steps in the Developer Portal to add the bot into a server, the bot can be activated by running the following command in a terminal at the root of this project.
```bash
python script.py
```

## Commands

This bot responds to commands sent via text channels in the server it is part of. Here are some key commands
```bash
$help               # returns a list of available commands and aliases
$join               # joins the call
$leave              # leaves the call
$play               # plays a random song
$stop               # stops playing music
$resume             # resumes music
$pause              # pauses music
```
