import asyncio
from playerBase import classEmojis

class Game:
  """A running instance of the game"""
  def __init__(self, channel):
    self.channel = channel
    self.players = {}
    self.actions = {}
    self.modifiedActions = {}
    self.running = False
    self.turns = 1
    self.takingCommands = False

  async def newGame(self):
    await self.channel.send("Created game")
    classMessage = "Type .join followed by a class emoji to join!"
    for emoji, _class in classEmojis.items():
      classMessage += '\n'
      classMessage += emoji + ': ' + _class.className()
    await self.channel.send(classMessage)

  async def startGame(self):
    await self.channel.send("\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_")
    await self.channel.send("**Game started!**")
    await self.printHealths(False)
    self.running = True
    while self.running:
      await self.gameLoop()

  async def endGame(self):
    self.running = False
    await self.channel.send("Ending game")

  async def gameLoop(self):
    await self.channel.send("\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_")
    await self.channel.send("**Turn " + str(self.turns) + "**")
    self.turns += 1

    self.takingCommands = True
    #
    #await self.enterAction(list(self.players.keys())[1], 2, [list(self.players.keys())[0]])
    #
    await asyncio.sleep(90)
    self.takingCommands = False
    if not self.running:
      return
    
    await self.channel.send("\* \* \* \* \* \* \* \* \* \* \* \*")
    self.phaseSkipTurns()
    self.phaseStartTurns()
    self.phaseModifyActions()
    self.phaseApplyEffects()
    self.phasePreDamage()
    self.phaseDealDamage()
    self.phaseModifyDamage()
    self.phaseTakeDamage()
    self.phasePostDamage()
    self.phaseEndTurns()
    await self.printActions()
    await self.channel.send("\* \* \* \* \* \* \* \* \* \* \* \*")
    await self.printHealths()
    self.actions.clear()
    self.players = {user:player for user, player in self.players.items() if player.alive}
    if len(self.players) == 1:
      await self.channel.send(list(self.players.values())[0].toString() + "**wins!**")
      await self.endGame()
      return
  
  async def addPlayer(self, user, _class):
    if not self.running:
      newPlayer = _class(user, self)
      self.players[user] = newPlayer
      await self.channel.send("Added player " + user.name + " as a " + newPlayer.className())

  async def info(self, user, _class):
    if not _class:
      player = self.players.get(user)
      if self.players.get(user):
        _class = player
      else:
        await self.channel.send("Specify a class for info")
        return
    toPrint = _class.getInfo()
    await self.channel.send(toPrint)

  async def enterAction(self, actingUser, whichAbility, targets):
    if self.running and self.takingCommands:
      player = self.players.get(actingUser)
      if not player:
        return
      targetPlayers = [self.players[target] for target in targets if target in self.players.keys()]
      abilityClass = player.ability1() if whichAbility == 1 else player.ability2()
      ability = player.doAbility(abilityClass, targetPlayers)
      if ability.canUse():
        self.actions[player] = ability
        await self.channel.send(player.toString() + " entered their action")
      else:
        await self.channel.send(player.toString() + " Invalid targets for ability")

  async def skipTurn(self, actingUser):
    if self.running and self.takingCommands:
      player = self.players.get(actingUser)
      if not player:
        return
      self.actions[player] = None
      await self.channel.send(player.toString() + " entered their action")

  def phaseSkipTurns(self):
    for player in self.players.values():
      if self.actions.get(player) == None:
        player.skipTurn()

  def phaseStartTurns(self):
    for player in self.players.values():
      player.startTurn()
    for user, action in self.actions.items():
      if action:
        action.startTurnEffect()
    for player in self.players.values():
      for effect in player.activeEffects:
        effect.startTurnEffect()

  def phaseModifyActions(self):
    self.modifiedActions = self.actions
    for player in self.players.values():
      player.modifyActions()
    for user, action in self.actions.items():
      if action:
        action.modifyActions()
    for player in self.players.values():
      for effect in player.activeEffects:
        effect.modifyActions()
    self.actions = self.modifiedActions

  def phaseApplyEffects(self):
    for player in self.players.values():
      player.applyEffects()
    for user, action in self.actions.items():
      if action:
        action.applyEffects()
    for player in self.players.values():
      for effect in player.activeEffects:
        effect.applyEffects()

  def phasePreDamage(self):
    for user, action in self.actions.items():
      if action:
        action.preDamageEffect()
    for player in self.players.values():
      player.preDamagePhase()
      for effect in player.activeEffects:
        effect.preDamageEffect()

  def phaseDealDamage(self):
    for user, action in self.actions.items():
      if action:
        action.damageEffect()
    for player in self.players.values():
      for effect in player.activeEffects:
        effect.damageEffect()

  def phaseModifyDamage(self):
    for player in self.players.values():
      player.modifyDamage()

  def phaseTakeDamage(self):
    for player in self.players.values():
      player.takeDamage()

  def phasePostDamage(self):
    for user, action in self.actions.items():
      if action:
        action.postEffect()
    for player in self.players.values():
      for effect in player.activeEffects:
        effect.postEffect()

  def phaseEndTurns(self):
    for player in self.players.values():
      player.endTurn()

  async def printActions(self):
    for player in self.players.values():
      ability = self.actions.get(player)
      if ability:
        targetsString = ", ".join([target.toString() for target in ability.targets])
        await self.channel.send(player.toString() + " used ability " + ability.abilityName() + " on " + targetsString)
      else:
        await self.channel.send(player.toString() + " skipped their turn")

  async def printHealths(self, doDrinks = True):
    for player in self.players.values():
      playerString = player.toString()
      if doDrinks:
        playerString += " drink " + str(player.damageTakenLastTurn)
      await self.channel.send(playerString)

