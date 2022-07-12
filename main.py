import os
import discord
from discord.ext import commands
from game.game import Game
from base.playerBase import classEmojis, classNames

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='.', description='Drunkgeons and Dragons Bot', intents=intents)

#Channel to game instance dictionary
games = {}

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
  await game.addPlayer(user, _class)

async def doInfo(game, user, _class):
  await game.info(user, _class)

async def doAbility(game, user, whichAbility, targets):
  if whichAbility == 1 or whichAbility == 2:
    await game.enterAction(user, whichAbility, targets)

async def doSkipTurn(game, user):
  await game.skipTurn(user)

# Quickly starts a new game with me and my alt account for dev purposes
async def debugGame():
  guild = bot.get_guild(932077177875337278)
  channel = guild.get_channel(936704274451296286)
  bobmowzieUser = guild.get_member(301435749729828867)
  caesicCultistUser = guild.get_member(747871773282009420)
  game = await doNewGame(channel)
  await doAddPlayer(game, bobmowzieUser, classNames['Druid'])
  await doAddPlayer(game, caesicCultistUser, classNames['Wizard'])
  await doStartGame(game)

@bot.event
async def on_ready():
  print('Logged in as {0}'.format(bot.user))
  # await debugGame()

@bot.command()
async def newGame(ctx):
  await doNewGame(ctx.channel)

@bot.command()
async def startGame(ctx):
  await doStartGame(games[ctx.channel])

@bot.command()
async def endGame(ctx):
  await doEndGame(games[ctx.channel])

@bot.command()
async def join(ctx, classInput: str):
  # Player can specify class name or emoji
  _class = classEmojis.get(classInput)
  if not _class:
    _class = classNames.get(classInput.capitalize())
  await doAddPlayer(games[ctx.channel], ctx.author, _class)

@bot.command()
async def info(ctx, classInput: str):
  # Player can specify class name or emoji
  _class = classEmojis.get(classInput)
  if not _class:
    _class = classNames.get(classInput.capitalize())
  await doInfo(games[ctx.channel], ctx.author, _class)

@bot.command(name='1')
async def ability1(ctx, *targets: discord.Member):
  await ctx.message.delete()
  await doAbility(games[ctx.channel], ctx.author, 1, targets)

@bot.command(name='2')
async def ability2(ctx, *targets: discord.Member):
  await ctx.message.delete()
  await doAbility(games[ctx.channel], ctx.author, 2, targets)

@bot.command(name='skip')
async def skipTurn(ctx):
  await ctx.message.delete()
  await doSkipTurn(games[ctx.channel], ctx.author)

bot.run(os.environ['TOKEN'])

