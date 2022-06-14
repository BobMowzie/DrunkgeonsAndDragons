from abc import ABC, abstractmethod
import math


def toSub(x):
    normal = "0123456789"
    sub_s = "₀₁₂₃₄₅₆₇₈₉"
    res = x.maketrans(''.join(normal), ''.join(sub_s))
    return x.translate(res)


class PlayerBase(ABC):
    """A player character class"""

    def __init__(self, user, game):
        self.user = user
        self.game = game
        self.team = None
        self.health = 15
        self.damageTakenThisTurn = 0
        self.damageTakenLastTurn = 0
        self.attackMultiplier = 1
        self.takeDamageMultiplier = 1
        self.takeDamageReduction = 0
        self.activeEffects = []
        self.alive = True
        self.curingClerics = []
        self.damageTaken = []  # List of (source player, amount) tuples
        self.damageDealt = {}  # Dict mapping target player to amount

    @classmethod
    @abstractmethod
    def ability1(cls):
        pass

    @classmethod
    @abstractmethod
    def ability2(cls):
        pass

    @classmethod
    def getInfo(cls):
        toPrint = "**" + cls.classEmoji() + " " + cls.className() + "**\n"
        toPrint += cls.classDescription() + "\n"
        toPrint += "**Ability 1: " + cls.ability1().abilityName() + "\n**"
        toPrint += cls.ability1().abilityDescription() + "\n"
        toPrint += "**Ability 2: " + cls.ability2().abilityName() + "\n**"
        toPrint += cls.ability2().abilityDescription() + "\n"
        return toPrint

    def doAbility(self, abilityClass, target):
        return abilityClass(self, target)

    def skipTurn(self):
        pass

    def startTurn(self):
        self.activeEffects = [effect for effect in self.activeEffects if effect.turnsRemaining > 0]

    def modifyActions(self):
        pass

    def applyEffects(self):
        if len(self.curingClerics) > 0:
            for cleric in self.curingClerics:
                cleric.blessings += len(self.activeEffects)
            self.activeEffects.clear()

    def preDamagePhase(self):
        pass

    def dealDamage(self, target, amount, source=None):
        amount = amount * self.attackMultiplier
        target.addDamageSource(amount, self, source)

    def addDamageSource(self, amount, damager, source=None):
        from classes.paladin import ShieldEffect
        blockingPaladins = [effect.caster for effect in self.activeEffects if isinstance(effect, ShieldEffect)]
        if len(blockingPaladins) > 0:
            blockedAmount = math.floor(amount / 2)
            for paladin in blockingPaladins:
                paladin.damageTaken.append((damager, blockedAmount))
                if amount > paladin.biggestAttack:
                    paladin.biggestAttack = amount
        else:
            self.damageTaken.append((damager, amount))

    def modifyDamage(self):
        self.damageTaken.sort(key=lambda x: x[1])

        from classes.cleric import DivineBarrierEffect
        largestBlockedSoFar = 0
        divineBarriers = [effect for effect in self.activeEffects if
                          isinstance(effect, DivineBarrierEffect) and effect.turnsRemaining > 0]
        for i in range(len(self.damageTaken)):
            source = self.damageTaken[i][0]
            amount = self.damageTaken[i][1]
            if amount > largestBlockedSoFar:
                largestBlockedSoFar = amount
                for dBarrier in divineBarriers:
                    dBarrier.turnsRemaining -= 1
                    divineBarriers = [barrier for barrier in divineBarriers if barrier.turnsRemaining >= 0]
            if len(divineBarriers) > 0:
                self.damageTaken[i] = (source, 0)

    def takeDamage(self):
        for player, amount in self.damageTaken:
            amount = max(0, amount - self.takeDamageReduction)
            amount = math.floor(amount * self.takeDamageMultiplier)
            self.health -= amount
            self.damageTakenThisTurn += amount
            if player.damageDealt.get(self):
                player.damageDealt[self] += amount
            else:
                player.damageDealt[self] = amount
            if self.health <= 0:
                self.health = 0
                self.alive = False

    def endTurn(self):
        self.damageTakenLastTurn = self.damageTakenThisTurn
        self.damageTakenThisTurn = 0
        self.attackMultiplier = 1
        self.takeDamageMultiplier = 1
        self.takeDamageReduction = 0
        for effect in self.activeEffects:
            effect.turnsRemaining = max(effect.turnsRemaining - 1, 0)
        self.curingClerics.clear()
        self.damageTaken.clear()
        self.damageDealt.clear()

    @classmethod
    def classDescription(cls):
        return ''

    @classmethod
    def className(cls):
        return ''

    @classmethod
    def classEmoji(cls):
        return ''

    def hasEffect(self, effectType):
        return any(isinstance(effect, effectType) for effect in self.activeEffects)

    def removeEffect(self, effectType):
        self.activeEffects = [effect for effect in self.activeEffects if not isinstance(effect, effectType)]

    def addEffect(self, effect):
        if len(self.curingClerics) > 0:
            for cleric in self.curingClerics:
                cleric.blessings += 1
            return
        self.activeEffects.append(effect)

    def toString(self):
        toReturn = self.classEmoji()
        resourceNumber = self.resourceNumber()
        if resourceNumber:
            toReturn += toSub(str(resourceNumber))
        toReturn += '❤️' + toSub(str(self.health))
        toReturn += "<@" + str(self.user.id) + "> "
        for effect in self.activeEffects:
            toReturn += effect.effectEmoji() + toSub(str(effect.turnsRemaining))
        return toReturn

    def resourceNumber(self):
        return None


from classes.barbarian import Barbarian
from classes.paladin import Paladin
from classes.wizard import Wizard
from classes.cleric import Cleric
from classes.druid import Druid
from classes.warlock import Warlock

classEmojis = {
    Barbarian.classEmoji(): Barbarian,
    Paladin.classEmoji(): Paladin,
    Wizard.classEmoji(): Wizard,
    Cleric.classEmoji(): Cleric,
    Druid.classEmoji(): Druid,
    Warlock.classEmoji(): Warlock
}

classNames = {
    Barbarian.className(): Barbarian,
    Paladin.className(): Paladin,
    Wizard.className(): Wizard,
    Cleric.className(): Cleric,
    Druid.className(): Druid,
    Warlock.className(): Warlock
}
