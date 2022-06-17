import asyncio
from playerBase import classEmojis
from gameevents import *


class Game:
    """A running instance of the game"""

    def __init__(self, channel):
        self.channel = channel
        self.players = {}
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
        # await self.enterAction(list(self.players.keys())[1], 2, [list(self.players.keys())[0]])
        #
        await asyncio.sleep(90)
        self.takingCommands = False
        if not self.running:
            return
        await self.channel.send("\* \* \* \* \* \* \* \* \* \* \* \*")

        phases = [
            PhaseStartTurns(),
            PhaseModifyActions(),
            PhaseApplyEffects(),
            PhasePreDamage(),
            PhaseDealDamage(),
            PhaseTakeDamage(),
            PhasePostDamage(),
            PhaseEndTurns()
        ]
        for phase in phases:
            self.doEvent(phase)

        await self.printActions()
        await self.channel.send("\* \* \* \* \* \* \* \* \* \* \* \*")
        await self.printHealths()
        self.players = {user: player for user, player in self.players.items() if player.alive}
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
                player.activeAbility = ability
                await self.channel.send(player.toString() + " entered their action")
            else:
                await self.channel.send(player.toString() + " Invalid targets for ability")

    async def skipTurn(self, actingUser):
        if self.running and self.takingCommands:
            player = self.players.get(actingUser)
            if not player:
                return
            player.activeAbility = None
            await self.channel.send(player.toString() + " entered their action")

    def doEvent(self, event):
        players = list(self.players.values())
        abilities = [player.activeAbility for player in players if player.activeAbility]
        effects = [effect for effect in (player.activeEffects for player in players)]
        subscribers = players + abilities + effects

        subscriptions = []
        for subscriber in subscribers:
            subscriptions.extend([sub for sub in subscriber.subscribedEvents if sub.eventClass == type(event)])

        subscriptions.sort(key=lambda sub: sub.order)
        for sub in subscriptions:
            sub.function(event)

    async def printActions(self):
        for player in self.players.values():
            ability = player.activeAbility
            if ability:
                targetsString = ", ".join([target.toString() for target in ability.targets])
                await self.channel.send(
                    player.toString() + " used ability " + ability.abilityName() + " on " + targetsString)
            else:
                await self.channel.send(player.toString() + " skipped their turn")

    async def printHealths(self, doDrinks=True):
        for player in self.players.values():
            playerString = player.toString()
            if doDrinks:
                playerString += " drink " + str(player.damageTakenLastTurn)
            await self.channel.send(playerString)
