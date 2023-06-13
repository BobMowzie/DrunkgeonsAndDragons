from abc import abstractmethod

from game.damageInstance import DamageInstance
from game.gameEvents import *
import math

from enum import Enum


class Team(Enum):
    Orange = "🧡"
    Yellow = "💛"
    Green = "💚"
    Blue = "💙"
    Purple = "💜"
    Black = "🖤"
    Brown = "🤎"
    White = "🤍"


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

        self.votekicks = {}

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
        self.activeAbilityLastTurn = None
        # For when other abilities change or add this players action during a turn. Sometimes more than one
        # ability per player is possible.
        self.modifiedAbilities = []
        self.modifiedAbilitiesLastTurn = []

        self.alive = True
        self.damageTaken = []  # List of DamageInstances
        self.damageDealt = []  # List of DamageInstances

        self.subscribeEvent(PhaseStartTurns, self.startTurn, -100)
        self.subscribeEvent(EventDealDamage, self.adjustDealDamage, 50)
        self.subscribeEvent(EventTakeDamage, self.adjustTakeDamage, -50)
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

    def setTeam(self, team):
        self.team = team

    def doAbility(self, whichAbility, targets):
        abilityClass = self.ability1() if whichAbility == 1 else self.ability2()
        ability = abilityClass(self, targets)
        canUse, message = ability.canUse()
        targetNames = [target.toString() for target in ability.targets]
        if canUse:
            self.activeAbility = ability
            message = "Using ability **" + ability.abilityName() + "**"
            if len(targetNames) > 0:
                message += " on " + ", ".join(targetNames) + "."
        return canUse, message

    def getAllActiveAbilities(self):
        abilities = [self.activeAbility]
        abilities.extend(self.modifiedAbilities)
        abilities = [ability for ability in abilities if ability and not ability.canceled]
        return abilities

    def startTurn(self, event):
        self.activeEffects = [effect for effect in self.activeEffects if effect.turnsRemaining > 0 or not effect.hasTurnsRemaining]

    def adjustDealDamage(self, event):
        if event.damageInstance.attacker == self:
            event.damageInstance.newAmount = max(0, event.damageInstance.amount + self.dealDamageAddition)
            event.damageInstance.newAmount = math.floor(event.damageInstance.amount * self.dealDamageMultiplier)

    def dealDamage(self, target, amount, source=None):
        damageInstance = DamageInstance(self, target, amount, source)
        self.damageDealt.append(damageInstance)
        event = EventDealDamage(damageInstance, self.game)
        self.game.doEvent(event)

        if not damageInstance.canceled:
            target = damageInstance.target
            target.damageTaken.append(damageInstance)

    def adjustTakeDamage(self, event):
        if event.damageInstance.target == self:
            event.damageInstance.newAmount = max(0, event.damageInstance.amount + self.takeDamageAddition)
            event.damageInstance.newAmount = math.floor(event.damageInstance.amount * self.takeDamageMultiplier)

    def takeDamage(self, event):
        self.damageTaken.sort(key=lambda di: di.amount)
        for damageInstance in self.damageTaken:
            event = EventTakeDamage(damageInstance, self.game)
            self.game.doEvent(event)

            if not damageInstance.canceled:
                amount = event.damageInstance.amount
                self.health -= amount
                self.damageTakenThisTurn += amount
                if self.health <= 0:
                    self.health = 0
                    self.alive = False
                    self.game.deadPlayers.append(self.user)

    def resetPlayer(self):
        self.modifiedAbilitiesLastTurn = self.modifiedAbilities
        self.modifiedAbilities.clear()
        self.activeAbilityLastTurn = self.activeAbility
        self.activeAbility = None
        self.damageTakenLastTurn = self.damageTakenThisTurn
        self.damageTakenThisTurn = 0
        self.dealDamageMultiplier = 1
        self.dealDamageAddition = 0
        self.takeDamageMultiplier = 1
        self.takeDamageAddition = 0
        for effect in self.activeEffects:
            effect.decrementTurnsRemaining()
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

    def getEffect(self, effectType):
        for effect in self.activeEffects:
            if isinstance(effect, effectType):
                return effect

    def getAllEffectsOfType(self, effectType):
        return [effect for effect in self.activeEffects if isinstance(effect, effectType)]

    def removeEffect(self, effectType):
        self.activeEffects = [effect for effect in self.activeEffects if not isinstance(effect, effectType)]

    def removeEffectInstance(self, effect):
        self.activeEffects.remove(effect)

    def addEffect(self, effect):
        event = EventApplyEffect(effect, self.game)
        self.game.doEvent(event)

        if not event.canceled:
            self.activeEffects.append(effect)

    def toString(self):
        toReturn = self.classEmoji()
        resourceNumber = self.resourceNumber()
        if resourceNumber:
            toReturn += toSub(str(resourceNumber))
        heart = '❤'
        if self.team:
            heart = self.team.value
        toReturn += heart
        toReturn += toSub(str(self.health))
        toReturn += "<@" + str(self.user.id) + "> "
        for effect in self.activeEffects:
            toReturn += effect.effectEmoji()
            if effect.hasTurnsRemaining:
                toReturn += toSub(str(effect.turnsRemaining))
        return toReturn

    def resourceNumber(self):
        return None


from classes.barbarian import Barbarian
from classes.paladin import Paladin
from classes.wizard import Wizard
from classes.cleric import Cleric
from classes.druid import Druid
from classes.warlock import Warlock
from classes.blademaster import Blademaster

classEmojis = {
    Barbarian.classEmoji(): Barbarian,
    Paladin.classEmoji(): Paladin,
    Wizard.classEmoji(): Wizard,
    Cleric.classEmoji(): Cleric,
    Druid.classEmoji(): Druid,
    Warlock.classEmoji(): Warlock,
    Blademaster.classEmoji(): Blademaster
}

classNames = {
    Barbarian.className(): Barbarian,
    Paladin.className(): Paladin,
    Wizard.className(): Wizard,
    Cleric.className(): Cleric,
    Druid.className(): Druid,
    Warlock.className(): Warlock,
    Blademaster.className(): Blademaster
}
