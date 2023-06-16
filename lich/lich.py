import random
from collections import Counter

from base.abilityBase import AbilityBase
from game.gameEvents import PhaseStartTurns

numOptions = 2


class Lich:
    """The lich class"""

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.possibleAbilities = []
        self.votes = {}
        self.chosenAbility = None

    def randomizeAbilities(self):
        self.possibleAbilities = random.sample(lichAbilities, numOptions)

    async def printOptions(self):
        message = "This turn, the " + self.icon() + "Lich can use\n"
        i = 0
        for ability in self.possibleAbilities:
            i += 1
            message += str(i) + ") **" + ability.abilityName() + "**: " + ability.abilityDescription() + "\n"
        message += "Dead players can use /1 or /2 to vote"
        await self.game.channel.send(message)

    def vote(self, player, number):
        if number > numOptions:
            return False, "There are only " + str(numOptions) + " abilities to choose from"
        self.votes[player] = number - 1
        return True, "Voted for ability **" + self.possibleAbilities[number - 1].abilityName() + "**"

    def chooseAbility(self):
        data = Counter(self.votes.values())
        counts = data.most_common()
        if len(counts) == 0 or len(counts) > 1 and counts[0][1] == counts[1][1]:
            return None
        winningOption = counts[0][0]
        abilityClass = self.possibleAbilities[winningOption]
        self.chosenAbility = abilityClass(self)

    def reset(self):
        self.possibleAbilities = []
        self.votes = {}
        self.chosenAbility = None

    @classmethod
    def icon(cls):
        return "👻"


#######################################
# Abilities
#######################################
class Excruciate(AbilityBase):
    def __init__(self, caster):
        AbilityBase.__init__(self, caster, None)

        self.subscribeEvent(PhaseStartTurns, self.startTurn, -99)

    @classmethod
    def abilityName(cls):
        return "Excruciate"

    @classmethod
    def abilityDescription(cls):
        return "All players take +1 damage from attacks this turn."

    def startTurn(self, event):
        for player in self.game.players.values():
            player.takeDamageAddition += 1


class Eternity(AbilityBase):
    def __init__(self, caster):
        AbilityBase.__init__(self, caster, None)

        self.subscribeEvent(PhaseStartTurns, self.endTurn, -99)

    @classmethod
    def abilityName(cls):
        return "Eternity"

    @classmethod
    def abilityDescription(cls):
        return "All status effects gain +1 duration."

    def endTurn(self, event):
        for player in self.game.players.values():
            for effect in player.activeEffects:
                if effect.timed:
                    effect.turnsRemaining += 1


class Enfeeble(AbilityBase):
    def __init__(self, caster):
        AbilityBase.__init__(self, caster, None)

        self.subscribeEvent(PhaseStartTurns, self.startTurn, -99)

    @classmethod
    def abilityName(cls):
        return "Enfeeble"

    @classmethod
    def abilityDescription(cls):
        return "All players deal half damage this turn (rounded down)."

    def startTurn(self, event):
        for player in self.game.players.values():
            player.dealDamageMultiplier *= 0.5


lichAbilities = [Excruciate, Eternity, Enfeeble]
