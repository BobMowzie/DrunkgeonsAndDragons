import os
from typing import List, Sequence, Optional

import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from game.game import Game
from base.playerBase import classEmojis, classNames

intents = discord.Intents.default()
intents.members = True

# Channel to game instance dictionary
games = {}


class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=guild)
            self.synced = True
        print(f"Logged in as {self.user}")
        await debugGame()


client = MyClient()
tree = app_commands.CommandTree(client)
guild = discord.Object(id=932077177875337278)

classChoices = [Choice(name=className, value=className) for className in classNames.keys()]


async def doNewGame(channel):
    newGame = Game(channel)
    games[channel] = newGame
    await newGame.newGame()
    return newGame


async def doEndGame(game):
    await game.endGame()
    del games[game.channel]


async def doStartGame(game):
    await game.startGame()


async def doAddPlayer(game, user, _class):
    return await game.addPlayer(user, _class)


def doInfo(game, user, _class):
    return game.info(user, _class)


def is_me(m):
    return m.author == client.user


async def doAllInfo(channel):
    await channel.purge(limit=100, check=is_me)
    for _class in classNames.values():
        toPrint = _class.getInfo()
        await channel.send(toPrint)
        await channel.send("\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_")


async def doAbility(game, user, whichAbility, targets):
    return await game.enterAction(user, whichAbility, targets)


async def doSkipTurn(game, user):
    return await game.skipTurn(user)


# Quickly starts a new game with me and my alt account for dev purposes
async def debugGame():
    thisGuild = client.get_guild(932077177875337278)
    channel = thisGuild.get_channel(936704274451296286)
    bobmowzieUser = thisGuild.get_member(301435749729828867)
    caesicCultistUser = thisGuild.get_member(747871773282009420)
    game = await doNewGame(channel)
    await doAddPlayer(game, bobmowzieUser, classNames['Warlock'])
    await doAddPlayer(game, caesicCultistUser, classNames['Warlock'])
    await doStartGame(game)


@tree.command(name="new_game", description="Create a new game.", guild=guild)
async def newGame(interaction: discord.Interaction):
    await interaction.response.send_message("Created game")
    await doNewGame(interaction.channel)


@tree.command(name="start_game", description="Start the game.", guild=guild)
async def startGame(interaction: discord.Interaction):
    await interaction.response.send_message("Game started!")
    await doStartGame(games[interaction.channel])


@tree.command(name="end_game", description="End the game.", guild=guild)
async def endGame(interaction: discord.Interaction):
    await interaction.response.send_message("Game ended")
    await doEndGame(games[interaction.channel])


@tree.command(name="join", description="Join the game in this channel.", guild=guild)
@app_commands.choices(class_input = classChoices)
async def join(interaction: discord.Interaction, class_input: str):
    # Player can specify class name or emoji
    _class = classEmojis.get(class_input)
    if not _class:
        _class = classNames.get(class_input.capitalize())
    result = await doAddPlayer(games[interaction.channel], interaction.user, _class)
    if result:
        await interaction.response.send_message("Added player " + interaction.user.name + " as a " + _class.className())
    else:
        await interaction.response.send_message("Can't join. Game is already running.")


@tree.command(name="info", description="View info and abilities for a specific class. "
                                       "Specify no class to view your current class.", guild=guild)
@app_commands.choices(class_input = classChoices)
async def info(interaction: discord.Interaction, class_input: Optional[str] = None):
    # Player can specify class name or emoji
    _class = classEmojis.get(class_input)
    if not _class:
        _class = classNames.get(class_input.capitalize())
    toPrint = doInfo(games[interaction.channel], interaction.user, _class)
    await interaction.response.send_message(toPrint, ephemeral=True)


@tree.command(name="all_info", description="View all class info and abilities.", guild=guild)
async def allInfo(interaction: discord.Interaction):
    await interaction.response.send_message("Printing all info", ephemeral=True)
    await doAllInfo(interaction.channel)


async def respondToAction(interaction: discord.Interaction, succeeded, message):
    statusEmoji = "???" if succeeded else "???"
    message = statusEmoji + " " + message
    await interaction.response.send_message(message, ephemeral=True)


@tree.command(name="1", description="Use ability 1.", guild=guild)
async def ability1(interaction: discord.Interaction, target: Optional[discord.User]):
    succeeded, message = await doAbility(games[interaction.channel], interaction.user, 1, [target])
    await respondToAction(interaction, succeeded, message)


@tree.command(name="2", description="Use ability 2.", guild=guild)
async def ability2(interaction: discord.Interaction, target: Optional[discord.User]):
    succeeded, message = await doAbility(games[interaction.channel], interaction.user, 2, [target])
    await respondToAction(interaction, succeeded, message)


@tree.command(name="skip", description="Skip your turn.", guild=guild)
async def skipTurn(interaction: discord.Interaction):
    succeeded, message = await doSkipTurn(games[interaction.channel], interaction.user)
    await respondToAction(interaction, succeeded, message)


client.run(os.environ['TOKEN'])
