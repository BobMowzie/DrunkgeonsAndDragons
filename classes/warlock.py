from math import ceil

from base.playerBase import PlayerBase
from base.abilityBase import AbilityBase
from base.effectBase import EffectBase
from game.gameEvents import PhaseDealDamage, PhaseApplyEffects, EventDealDamage


class Warlock(PlayerBase):
    def __init__(self, user, game):
        PlayerBase.__init__(self, user, game)
        self.soulboundEffect = None

    @classmethod
    def className(cls):
        return 'Warlock'

    @classmethod
    def classEmoji(cls):
        return '💀'

    @classmethod
    def classDescription(cls):
        return "High-risk, high-reward offensive class. Sacrifices their own health to deal damage."

    @classmethod
    def ability1(cls):
        return EldritchBlast

    @classmethod
    def ability2(cls):
        return Soullink


#######################################
# Abilities
#######################################
class EldritchBlast(AbilityBase):
    def __init__(self, caster: Warlock, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseDealDamage, self.damageEffect, 0)

    @classmethod
    def abilityName(cls):
        return "Eldritch Blast"

    @classmethod
    def abilityDescription(cls):
        return 'Deal 3 damage to a target and 1 damage to yourself.'

    def damageEffect(self, event):
        target = self.targets[0]
        self.caster.dealDamage(target, 3)
        self.caster.dealDamage(self.caster, 1)

    def actionText(self):
        return f"dealing 3 damage to them and 1 damage to themselves"


class Soullink(AbilityBase):
    def __init__(self, caster: Warlock, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)

    @classmethod
    def abilityName(cls):
        return "Soullink"

    @classmethod
    def abilityDescription(cls):
        return 'Soullink (⛓️) to a target for 2 turns. Whenever you are dealt damage, they are dealt half of that damage too (rounded up).'

    def applyEffects(self, events):
        target = self.targets[0]
        soulboundEffect = self.caster.soulboundEffect
        if soulboundEffect and soulboundEffect in soulboundEffect.target.activeEffects:
            soulboundEffect.target.removeEffectInstance(soulboundEffect)
        self.caster.soulboundEffect = SoulboundEffect(self.caster, target, 2)
        target.addEffect(self.caster.soulboundEffect)

    def actionText(self):
        return f"linking (⛓️) incoming damage to them for 2 turns"


#######################################
# Effects
#######################################
class SoulboundEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

        self.subscribeEvent(EventDealDamage, self.dealDamageEvent, 99)

    @classmethod
    def effectName(cls):
        return "Soullink"

    @classmethod
    def effectEmoji(cls):
        return '⛓️'

    def dealDamageEvent(self, event):
        damageInstance = event.damageInstance
        if isinstance(damageInstance.target, Warlock) \
                and damageInstance.target.soulboundEffect == self\
                and not isinstance(damageInstance.source, SoulboundEffect)\
                and not damageInstance.canceled:
            self.caster.dealDamage(self.target, ceil(damageInstance.amount / 2.0), self)
