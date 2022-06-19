from base.playerBase import PlayerBase
from base.abilityBase import AbilityBase
from base.effectBase import EffectBase
from game.gameEvents import *


class Cleric(PlayerBase):
    def __init__(self, user, game):
        PlayerBase.__init__(self, user, game)
        self.blessings = 1

    @classmethod
    def className(cls):
        return 'Cleric'

    @classmethod
    def classEmoji(cls):
        return '📖'

    @classmethod
    def classDescription(cls):
        return "Support class. Purely defensive. Cleanses status effects from both allies and enemies to gain blessings for Divine Barriers."

    @classmethod
    def ability1(cls):
        return Cure

    @classmethod
    def ability2(cls):
        return DivineBarrier

    def resourceNumber(self):
        return self.blessings


#######################################
# Abilities
#######################################
class Cure(AbilityBase):
    def __init__(self, caster: Cleric, targets):
        AbilityBase.__init__(self, caster, targets)

        # Separated so that if two clerics cleanse the same target, both get the blessings
        self.subscribeEvent(PhaseStartTurns, self.countBlessings, -99)
        self.subscribeEvent(PhaseStartTurns, self.removeEffects, -98)
        self.subscribeEvent(EventApplyEffect, self.applyEffectsEvent, 0)

    @classmethod
    def abilityName(cls):
        return "Cleanse"

    @classmethod
    def abilityDescription(cls):
        return "Clear all status effects (harmful and beneficial) from a target and prevent the target from receiving any new status effects this turn. Each effect cleansed grants one blessing to the Cleric."

    def countBlessings(self, event):
        target = self.targets[0]
        self.caster.blessings += len(target.activeEffects)

    def removeEffects(self, event):
        target = self.targets[0]
        target.activeEffects.clear()

    def applyEffectsEvent(self, event):
        target = self.targets[0]
        if event.target == target and not event.canceled:
            event.newCanceled = True
            self.caster.blessings += 1

    def canUse(self):
        return len(self.targets) == 1


class DivineBarrier(AbilityBase):
    def __init__(self, caster: Cleric, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)

    @classmethod
    def abilityName(cls):
        return "Divine Barrier"

    @classmethod
    def abilityDescription(cls):
        return "Expend all blessings to create a barrier on a target. For however many blessings spent, the barrier blocks that many hits of damage (smallest first)."

    def applyEffects(self, event):
        target = self.targets[0]
        newBarrier = DivineBarrierEffect(self.caster, target, self.caster.blessings)
        self.caster.blessings = 1

        oldBarrier = target.getEffect(DivineBarrierEffect)
        if oldBarrier:
            if oldBarrier.turnsRemaining < newBarrier.turnsRemaining:
                target.removeEffect(DivineBarrierEffect)
                target.addEffect(newBarrier)
        else:
            target.addEffect(newBarrier)

    def canUse(self):
        return len(self.targets) == 1


#######################################
# Effects
#######################################
class DivineBarrierEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)
        self.timed = False
        self.largestBlockedSoFar = 0

        self.subscribeEvent(PhaseStartTurns, self.startTurn, 0)
        self.subscribeEvent(EventTakeDamage, self.takeDamageEvent, 1)

    @classmethod
    def effectName(cls):
        return "Divine Barrier"

    @classmethod
    def effectEmoji(cls):
        return '✝️'

    def startTurn(self, event):
        self.largestBlockedSoFar = 0

    def takeDamageEvent(self, event):
        damageInstance = event.damageInstance
        if self.turnsRemaining > 0 and not damageInstance.canceled and damageInstance.target == self.target:
            event.damageInstance.newCanceled = True
            amount = damageInstance.amount
            if amount > self.largestBlockedSoFar:
                self.largestBlockedSoFar = amount
                self.turnsRemaining = max(self.turnsRemaining - 1, 0)
