from base.playerBase import PlayerBase
from base.abilityBase import AbilityBase
from base.effectBase import EffectBase
from game.gameEvents import *


class Blademaster(PlayerBase):
    def __init__(self, user, game):
        PlayerBase.__init__(self, user, game)
        self.marks = []

    @classmethod
    def className(cls):
        return 'Blademaster'

    @classmethod
    def classEmoji(cls):
        return '⚔'

    @classmethod
    def classDescription(cls):
        return "Offensive class that can attack multiple times or multiple targets in one turn."

    @classmethod
    def ability1(cls):
        return Dualslash

    @classmethod
    def ability2(cls):
        return Omnislash


#######################################
# Abilities
#######################################
class Dualslash(AbilityBase):
    def __init__(self, caster: Blademaster, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseApplyEffects, self.applyEffect, 0)
        self.subscribeEvent(PhaseDealDamage, self.damageEffect, 0)

    @classmethod
    def abilityName(cls):
        return "Dualslash"

    @classmethod
    def abilityDescription(cls):
        return 'Attack a target twice for 1 damage each hit. Mark (🩸) the target.'

    def applyEffect(self, event):
        target = self.targets[0]
        marks = [effect for effect in target.getAllEffectsOfType(MarkedEffect) if effect.caster == self.caster]
        if len(marks) == 0:
            target.addEffect(MarkedEffect(self.caster, target))

    def damageEffect(self, event):
        target = self.targets[0]
        self.caster.dealDamage(target, 1, self)
        self.caster.dealDamage(target, 1, self)


class Omnislash(AbilityBase):
    def __init__(self, caster: Blademaster, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseDealDamage, self.dealDamage, 0)

    @classmethod
    def abilityName(cls):
        return "Omnislash"

    @classmethod
    def abilityDescription(cls):
        return 'Deal 2 damage to all marked players, then remove all marks.'

    @classmethod
    def maxNumTargets(cls):
        return 0

    @classmethod
    def minNumTargets(cls):
        return 0

    def dealDamage(self, event):
        for player in self.game.getPlayers():
            if player == self:
                continue
            marks = [effect for effect in player.getAllEffectsOfType(MarkedEffect) if effect.caster == self.caster]
            if len(marks) > 0:
                self.caster.dealDamage(player, 2, self)
                for effect in marks:
                    player.removeEffectInstance(effect)

#######################################
# Effects
#######################################
class MarkedEffect(EffectBase):
    def __init__(self, caster, target):
        EffectBase.__init__(self, caster, target, 0)
        self.timed = False
        self.hasTurnsRemaining = False

    @classmethod
    def effectName(cls):
        return "Marked"

    @classmethod
    def effectEmoji(cls):
        return '🩸'


