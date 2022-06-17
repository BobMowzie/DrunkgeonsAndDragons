from playerBase import PlayerBase
from abilityBase import AbilityBase
from effectBase import EffectBase
from gameevents import *


class Wizard(PlayerBase):
    def __init__(self, user, game):
        PlayerBase.__init__(self, user, game)
        self.power = 1

        self.subscribeEvent(PhaseStartTurns, self.startTurn, 0)
        self.subscribeEvent(PhaseEndTurns, self.endTurn, 0)

    @classmethod
    def className(cls):
        return 'Wizard'

    @classmethod
    def classEmoji(cls):
        return '🪄'

    @classmethod
    def classDescription(cls):
        return "Offensive but fragile class that charges up power by skipping turns and unleashes it in powerful " \
               "spells. Power decreases by 1 if they take damage. Power cannot go below 1. "

    @classmethod
    def ability1(cls):
        return Fireball

    @classmethod
    def ability2(cls):
        return Incinerate

    def startTurn(self):
        if not self.activeAbility:
            if self.damageTakenThisTurn == 0:
                self.power += 2

    def endTurn(self):
        if self.damageTakenThisTurn > 0 and self.power > 1:
            self.power -= 1
        PlayerBase.endTurn(self)

    def resourceNumber(self):
        return self.power


#######################################
# Abilities
#######################################
class Fireball(AbilityBase):
    def __init__(self, caster: Wizard, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseDealDamage, self.damageEffect, 0)

    @classmethod
    def abilityName(cls):
        return "Fireball"

    @classmethod
    def abilityDescription(cls):
        return 'Spend all your power to deal that much damage to a target.'

    def damageEffect(self):
        target = self.targets[0]
        self.caster.dealDamage(target, self.caster.power)
        self.caster.power = 1

    def canUse(self):
        return len(self.targets) == 1 and self.targets[0] != self.caster


class Incinerate(AbilityBase):
    def __init__(self, caster: Wizard, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)

    @classmethod
    def abilityName(cls):
        return "Incinerate"

    @classmethod
    def abilityDescription(cls):
        return 'Spend all your power to burn your target for that many turns.'

    def applyEffects(self):
        target = self.targets[0]
        target.addEffect(BurnEffect(self.caster, target, self.caster.power))
        self.caster.power = 1

    def canUse(self):
        return len(self.targets) == 1 and self.targets[0] != self.caster


#######################################
# Effects
#######################################
class BurnEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

        self.subscribeEvent(PhaseDealDamage, self.damageEffect, 0)

    def damageEffect(self):
        self.caster.dealDamage(self.target, 1)

    @classmethod
    def effectName(cls):
        return "Burn"

    @classmethod
    def effectEmoji(cls):
        return '🔥'
