from base.playerBase import PlayerBase
from base.abilityBase import AbilityBase
from base.effectBase import EffectBase
from game.gameEvents import *


class Wizard(PlayerBase):
    def __init__(self, user, game):
        PlayerBase.__init__(self, user, game)
        self.power = 1

        self.subscribeEvent(PhaseEndTurns, self.endTurnEvent, 0)

    @classmethod
    def className(cls):
        return 'Wizard'

    @classmethod
    def classEmoji(cls):
        return '🪄'

    @classmethod
    def classDescription(cls):
        return "Offensive but fragile class that charges up power by skipping turns and unleashes it in powerful " \
               "spells. Skip your turn to gain 2 power, but lose 1 power instead if you take damage. Power cannot go below 1. "

    @classmethod
    def ability1(cls):
        return Fireball

    @classmethod
    def ability2(cls):
        return Incinerate

    def endTurnEvent(self, event):
        if not self.activeAbility:
            if self.damageTakenThisTurn == 0:
                self.power += 2
        if self.damageTakenThisTurn > 0 and self.power > 1:
            self.power -= 1

    def resourceNumber(self):
        return self.power


#######################################
# Abilities
#######################################
class Fireball(AbilityBase):
    def __init__(self, caster: Wizard, targets):
        AbilityBase.__init__(self, caster, targets)
        self.damageDealt = 0

        self.subscribeEvent(PhaseDealDamage, self.damageEffect, 0)

    @classmethod
    def abilityName(cls):
        return "Fireball"

    @classmethod
    def abilityDescription(cls):
        return 'Spend all your power to deal that much damage to a target.'

    def damageEffect(self, event):
        target = self.targets[0]
        self.caster.dealDamage(target, self.caster.power, self)
        self.damageDealt = self.caster.power
        self.caster.power = 1

    def actionText(self):
        return f"dealing {self.damageDealt} damage"


class Incinerate(AbilityBase):
    def __init__(self, caster: Wizard, targets):
        AbilityBase.__init__(self, caster, targets)

        self.numTurns = 0

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)

    @classmethod
    def abilityName(cls):
        return "Incinerate"

    @classmethod
    def abilityDescription(cls):
        return 'Spend all your power to Burn (🔥) your target for that many turns.'

    def applyEffects(self, event):
        target = self.targets[0]
        target.addEffect(BurnEffect(self.caster, target, self.caster.power))
        self.numTurns = self.caster.power
        self.caster.power = 1

    def actionText(self):
        toReturn = f"burning (🔥) them for {self.numTurns} turn"
        if self.numTurns > 1:
            toReturn += "s"
        return toReturn


#######################################
# Effects
#######################################
class BurnEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

        self.subscribeEvent(PhaseDealDamage, self.damageEffect, 0)

    def damageEffect(self, event):
        self.caster.dealDamage(self.target, 1, self)

    @classmethod
    def effectName(cls):
        return "Burn"

    @classmethod
    def effectEmoji(cls):
        return '🔥'
