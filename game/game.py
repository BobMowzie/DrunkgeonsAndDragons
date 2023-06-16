import asyncio
import itertools
import math

from base.playerBase import classEmojis, PlayerBase
from debug.debugUser import DebugUser
from game.gameEvents import *
from lich.lich import Lich


class Game:
    """A running instance of the game"""

    def __init__(self, channel):
        self.maxTurnLength = 20

        self.channel = channel
        self.players = {}
        self.deadPlayers = {}
        self.running = False
        self.turns = 1
        self.takingCommands = False

        self.playersActedThisTurn = set()

        self.lich = None

    async def newGame(self):
        classMessage = "Type /join followed by a class name to join!"
        for emoji, _class in classEmojis.items():
            classMessage += '\n'
            classMessage += emoji + ': ' + _class.className()
        await self.channel.send(classMessage)

    async def startGame(self):
        if self.running:
            return
        self.running = True
        await self.channel.send("\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_")
        await self.printHealths(False)
        while self.running:
            await self.gameLoop()

    async def endGame(self):
        self.running = False
        self.players.clear()
        self.deadPlayers.clear()
        self.turns = 1
        self.playersActedThisTurn = set()

    async def gameLoop(self):
        await self.channel.send("\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_")
        await self.channel.send("**Turn " + str(self.turns) + "**")
        self.turns += 1

        if len(self.deadPlayers) > 0 and not self.lich:
            self.lich = Lich(self)
            await self.channel.send("The " + Lich.icon() + "Lich appeared!")

        if self.lich:
            self.lich.randomizeAbilities()
            await self.lich.printOptions()

        self.playersActedThisTurn.clear()
        self.takingCommands = True

        # debug
        # await self.enterAction(list(self.players.keys())[1], 2, [list(self.players.keys())[0]])
        #
        for user in self.players.keys():
            if isinstance(user, DebugUser):
                await user.chooseAbility()
        for user in self.deadPlayers.keys():
            if isinstance(user, DebugUser):
                await user.chooseAbility()

        turnTimer = 0
        while turnTimer < self.maxTurnLength:
            await asyncio.sleep(1)
            turnTimer += 1
            if len(self.playersActedThisTurn) >= len(self.players) + len(self.deadPlayers):
                break
        await asyncio.sleep(5)

        self.takingCommands = False
        if not self.running:
            return
        await self.channel.send("\* \* \* \* \* \* \* \* \* \* \* \*")

        if self.lich:
            self.lich.chooseAbility()

        phases = [
            PhaseStartTurns(self),
            PhaseModifyActions(self),
            PhaseApplyEffects(self),
            PhasePreDamage(self),
            PhaseDealDamage(self),
            PhaseTakeDamage(self),
            PhasePostDamage(self),
            PhaseEndTurns(self)
        ]
        for phase in phases:
            self.doEvent(phase)

        #DEBUG
        if self.turns == 2:
            list(self.players.values())[0].die()
            list(self.players.values())[1].die()
            list(self.players.values())[2].die()

        for player in self.getLivingPlayers():
            player.resetPlayer()

        await self.printActions()
        await self.channel.send("\* \* \* \* \* \* \* \* \* \* \* \*")
        await self.printHealths()

        self.players = {user: player for user, player in self.players.items() if player.alive}
        if len(self.players) == 0:
            await self.channel.send("**Draw!**")
            await self.endGame()
            return
        teams = set([player.team for player in self.getLivingPlayers()])
        if len(teams) == 1:
            # Only 1 team left! But it could be None if all players left are teamless
            winningTeam = list(teams)[0]
            if winningTeam is None:
                if len(self.players) == 1:
                    await self.channel.send(list(self.getLivingPlayers())[0].toString() + "**wins!**")
                    await self.endGame()
                    return
            else:
                await self.channel.send("**" + winningTeam.name + " team wins!**")
                await self.endGame()
                return

        if self.lich:
            self.lich.reset()

    def hasPlayer(self, user):
        return user in self.players.keys() or user in self.deadPlayers.keys()

    def getPlayerFromUser(self, user):
        player: PlayerBase = None
        if user in self.players.keys():
            player = self.players[user]
        elif user in self.deadPlayers.keys():
            player = self.deadPlayers[user]
        return player

    async def addPlayer(self, user, _class, team=None):
        if not self.running:
            newPlayer = _class(user, self)
            newPlayer.setTeam(team)
            self.players[user] = newPlayer
            return True
        return False

    async def removePlayer(self, user):
        if user in self.players.keys():
            del self.players[user]
            return True
        elif user in self.deadPlayers.keys():
            del self.deadPlayers[user]
            return True
        return False

    async def votekick(self, user, target):
        userPlayer: PlayerBase = self.getPlayerFromUser(user)
        if not userPlayer:
            return False, "User not in game"
        targetPlayer: PlayerBase = self.getPlayerFromUser(target)
        if targetPlayer:
            targetPlayer.votekicks = {u for u in targetPlayer.votekicks if self.hasPlayer(u)}
            targetPlayer.votekicks.add(user)
            neededVotes = math.ceil(2.0 * (len(self.players) + len(self.deadPlayers)) / 3.0)
            if len(targetPlayer.votekicks) >= neededVotes:
                await self.removePlayer(user)
                return True, "Kicked player " + target.name
            return True, "Votekick progress for " + target.name + ": " + str(len(targetPlayer.votekicks)) + "/" + str(neededVotes)
        return False, "Target not in game"

    def info(self, user, _class):
        if not _class:
            player = self.players.get(user)
            if self.players.get(user):
                _class = player
            else:
                return "Specify a class for info"
        toPrint = _class.getInfo()
        return toPrint

    async def printEnteredAction(self, player):
        if player.alive:
            await self.channel.send(player.toString() + " entered their action.")
        else:
            if isinstance(player.user, DebugUser):
                playerString = player.user.name
            else:
                playerString = "<@" + str(player.user.id) + ">"
            await self.channel.send(playerString + " voted.")

    def checkAction(self, actingUser):
        if not self.running:
            return False, "Game hasn't started yet."

        player = self.getPlayerFromUser(actingUser)
        if not player:
            return False, "You are not a player in this game."

        if not self.takingCommands:
            return False, "Please wait for the next turn to begin."

        return True, ""

    async def enterAction(self, actingUser, whichAbility, targets):
        passed, message = self.checkAction(actingUser)
        if not passed:
            return False, message

        if whichAbility != 1 and whichAbility != 2:
            return False, f"Invalid ability number {whichAbility}. Please choose ability 1 or 2."

        player = self.getPlayerFromUser(actingUser)

        # If dead, vote for lich ability
        if player in self.deadPlayers.values() and self.lich:
            succeeded, message = self.lich.vote(player, whichAbility)
        else:
            # If alive, use own ability
            targetPlayers = []
            for target in targets:
                if not target:
                    continue
                if target in self.deadPlayers.values():
                    return False, f"{target.name} is dead and cannot be targeted."
                targetPlayer = self.players.get(target)
                if not targetPlayer:
                    return False, f"{target.name} is not a player in this game."
                targetPlayers.append(targetPlayer)
            succeeded, message = player.doAbility(whichAbility, targetPlayers)

        if succeeded:
            self.playersActedThisTurn.add(player)
            await self.printEnteredAction(player)
        return succeeded, message

    async def skipTurn(self, actingUser):
        passed, message = self.checkAction(actingUser)
        if not passed:
            return False, message

        player = self.getPlayerFromUser(actingUser)
        player.activeAbilities = []
        self.playersActedThisTurn.add(player)
        await self.printEnteredAction(player)
        return True, "Skipping turn."

    def doEvent(self, event):
        event.beginEvent()

        players = self.getLivingPlayers()
        abilities = []
        if self.lich and self.lich.chosenAbility:
            abilities.append(self.lich.chosenAbility)
        for player in players:
            abilities.extend(player.getAllActiveAbilities())
        effects = []
        for player in players:
            effects.extend(player.activeEffects)

        subscriptions = []
        for subscriber in itertools.chain(players, abilities, effects):
            subscriptions.extend([sub for sub in subscriber.subscribedEvents if sub.eventClass == type(event)])

        # Run all event subscriptions in order. If two subscriptions have the same order, sort them by subscriber type.
        # This way, all effects and abilities of the same type will trigger at once.
        subscriptions.sort(key=lambda sub: (sub.order, type(sub.subscriber).__name__))
        prevSubClass = None
        for sub in subscriptions:
            # Check if this iteration is between subscriber types
            subClass = type(sub.subscriber)
            if subClass != prevSubClass:
                event.betweenSubscriberTypes()
                prevSubClass = subClass

            # Stop the event if it was canceled
            if event.canceled:
                break

            # Otherwise, do the subscribed function
            sub.function(event)
        event.betweenSubscriberTypes()
        event.endEvent()

    async def printActions(self):
        if self.lich:
            if self.lich.chosenAbility:
                message = "The " + Lich.icon() + "Lich used ability **"
                message += self.lich.chosenAbility.abilityName() + "**: "
                message += self.lich.chosenAbility.abilityDescription()
                await self.channel.send(message)
            else:
                await self.channel.send("The " + Lich.icon() + "Lich had a draw and skipped its turn")

        for player in self.getPlayersSortedByTeam():
            ability = player.activeAbilityLastTurn
            if ability:
                message = player.toString() + " used ability **" + ability.abilityName() + "**"
                if len(ability.targets) > 0:
                    targetsString = ", ".join([target.toString() for target in ability.targets])
                    message += " on " + targetsString
                await self.channel.send(message)

            else:
                await self.channel.send(player.toString() + " skipped their turn")

    async def printHealths(self, doDrinks=True):
        for player in self.getPlayersSortedByTeam():
            playerString = player.toString()
            damageMsg = playerString
            if doDrinks:
                damageMsg += " took " + str(player.damageTakenLastTurn) + " damage"
            await self.channel.send(damageMsg)
            if not player.alive:
                deathMsg = playerString + " **died!**"
                await self.channel.send(deathMsg)

    def getLivingPlayers(self):
        return list(self.players.values())

    def getPlayersSortedByTeam(self):
        return sorted(self.getLivingPlayers(), key=lambda p: p.team.value if p.team else "")
