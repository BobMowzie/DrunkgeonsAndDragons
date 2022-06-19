from base.playerBase import PlayerBase
from base.abilityBase import AbilityBase
import math
from game.gameEvents import *


class Paladin(PlayerBase):
    def __init__(self, user, game):
        PlayerBase.__init__(self, user, game)
        self.biggestAttack = 0
        self.biggestAttackLastTurn = 0

        self.subscribeEvent(EventTakeDamage, self.takeDamageEvent, 50)

    @classmethod
    def className(cls):
        return 'Paladin'

    @classmethod
    def classDescription(cls):
        return 'Tank class. Turns defense into offense.'

    @classmethod
    def ability1(cls):
        return Shield

    @classmethod
    def ability2(cls):
        return Retribution

    @classmethod
    def classEmoji(cls):
        return '🛡️'

    def resourceNumber(self):
        return 1 + self.biggestAttackLastTurn

    def takeDamageEvent(self, event):
        if event.target == self:
            if event.amount > self.biggestAttack:
                self.biggestAttack = event.amount

    def endTurn(self):
        self.biggestAttackLastTurn = self.biggestAttack
        self.biggestAttack = 0


#######################################
# Abilities
#######################################
class Shield(AbilityBase):
    def __init__(self, caster: Paladin, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(EventDealDamage, self.dealDamageEvent, -99)
        self.subscribeEvent(EventTakeDamage, self.takeDamageEvent, 51)

    @classmethod
    def abilityName(cls):
        return "Shield"

    @classmethod
    def abilityDescription(cls):
        return "Redirect all incoming damage on a target player onto you. That damage is halved (rounded down)."

    def dealDamageEvent(self, event):
        target = self.targets[0]
        damageInstance = event.damageInstance
        if damageInstance.target == target\
                and not isinstance(damageInstance.source, Shield)\
                and not damageInstance.canceled:
            damageInstance.newCanceled = True
            damageInstance.attacker.dealDamage(self.caster, damageInstance.originalAmount, self)

    def takeDamageEvent(self, event):
        damageInstance = event.damageInstance
        if damageInstance.target == self.caster and damageInstance.source == self:
            blockedAmount = math.floor(damageInstance.amount / 2)
            damageInstance.newAmount = blockedAmount

    def canUse(self):
        return len(self.targets) == 1


class Retribution(AbilityBase):
    def __init__(self, caster: Paladin, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseDealDamage, self.damageEffect, 0)

    @classmethod
    def abilityName(cls):
        return "Retribution"

    @classmethod
    def abilityDescription(cls):
        return "Deal damage to a target equal to the largest single hit of damage you took or blocked last turn, plus 1."

    def damageEffect(self, event):
        target = self.targets[0]
        self.caster.dealDamage(target, self.caster.biggestAttackLastTurn + 1, self)

    def canUse(self):
        return len(self.targets) == 1 and self.targets[0] != self.caster

