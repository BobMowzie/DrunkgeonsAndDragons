from abc import abstractmethod

from damageInstance import DamageInstance
from gameEvents import *
import math


def toSub(x):
    normal = "0123456789"
    sub_s = "₀₁₂₃₄₅₆₇₈₉"
    res = x.maketrans(''.join(normal), ''.join(sub_s))
    return x.translate(res)


class PlayerBase(EventSubscriber):
    """A player character class"""

    def __init__(self, user, game):
        super().__init__()
        self.user = user
        self.game = game
        self.team = None
        self.health = 15
        self.damageTakenThisTurn = 0
        self.damageTakenLastTurn = 0

        self.dealDamageMultiplier = 1
        self.dealDamageAddition = 0
        self.takeDamageMultiplier = 1
        self.takeDamageAddition = 0

        self.activeEffects = []
        self.activeAbility = None
        self.alive = True
        self.curingClerics = []
        self.damageTaken = []  # List of DamageInstances
        self.damageDealt = []  # List of DamageInstances

        self.subscribeEvent(PhaseStartTurns, self.startTurn, -100)
        self.subscribeEvent(EventDealDamage, self.adjustDealDamage, 50)
        self.subscribeEvent(EventTakeDamage, self.adjustTakeDamage, 50)
        self.subscribeEvent(PhaseTakeDamage, self.takeDamage, 100)

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

    def startTurn(self, event):
        self.activeEffects = [effect for effect in self.activeEffects if effect.turnsRemaining > 0]

    def modifyActions(self):
        pass

    def applyEffects(self):
        if len(self.curingClerics) > 0:
            for cleric in self.curingClerics:
                cleric.blessings += len(self.activeEffects)
            self.activeEffects.clear()

    def adjustDealDamage(self, event):
        event.damageInstance.amount = max(0, event.damageInstance.amount + self.dealDamageAddition)
        event.damageInstance.amount = math.floor(event.damageInstance.amount * self.dealDamageMultiplier)

    def dealDamage(self, target, amount, source=None):
        damageInstance = DamageInstance(self, target, amount, source)
        self.damageDealt.append(damageInstance)
        event = EventDealDamage(damageInstance)
        self.game.doEvent(event)

        if not damageInstance.canceled:
            target = damageInstance.target
            target.damageTaken.append(damageInstance)

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

    def adjustTakeDamage(self, event):
        event.damageInstance.amount = max(0, event.damageInstance.amount + self.takeDamageAddition)
        event.damageInstance.amount = math.floor(event.damageInstance.amount * self.takeDamageMultiplier)

    def takeDamage(self, event):
        for damageInstance in self.damageTaken:
            event = EventTakeDamage(damageInstance)
            self.game.doEvent(event)

            if not damageInstance.canceled:
                amount = event.damageInstance.amount
                self.health -= amount
                self.damageTakenThisTurn += amount
                if self.health <= 0:
                    self.health = 0
                    self.alive = False

    def resetPlayer(self):
        self.activeAbility = None
        self.damageTakenLastTurn = self.damageTakenThisTurn
        self.damageTakenThisTurn = 0
        self.dealDamageMultiplier = 1
        self.takeDamageMultiplier = 1
        self.takeDamageAddition = 0
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
