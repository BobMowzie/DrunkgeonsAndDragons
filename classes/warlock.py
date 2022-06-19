from playerBase import PlayerBase
from abilityBase import AbilityBase
from effectBase import EffectBase


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
        return Soulbind

    def addDamageSource(self, amount, damager, source=None):
        if not isinstance(source, SoulboundEffect):
            if self.soulboundEffect:
                target = self.soulboundEffect.target
                if self.soulboundEffect in target.activeEffects:
                    target.addDamageSource(amount, self, self.soulboundEffect)
            PlayerBase.addDamageSource(self, amount, damager, source)


#######################################
# Abilities
#######################################
class EldritchBlast(AbilityBase):
    def __init__(self, caster: Warlock, targets):
        AbilityBase.__init__(self, caster, targets)

    @classmethod
    def abilityName(cls):
        return "Eldritch Blast"

    @classmethod
    def abilityDescription(cls):
        return 'Deal 3 damage to a target and 1 damage to yourself.'

    def damageEffect(self):
        target = self.targets[0]
        self.caster.dealDamage(target, 3)
        self.caster.dealDamage(self.caster, 1)

    def canUse(self):
        return len(self.targets) == 1 and self.targets[0] != self.caster


class Soulbind(AbilityBase):
    def __init__(self, caster: Warlock, targets):
        AbilityBase.__init__(self, caster, targets)

    @classmethod
    def abilityName(cls):
        return "Soulbind"

    @classmethod
    def abilityDescription(cls):
        return 'Bind your soul to a target for 3 turns. Whenever you take damage, they take damage too.'

    def applyEffects(self):
        target = self.targets[0]
        self.caster.soulboundEffect = SoulboundEffect(self.caster, target, 3)
        target.addEffect(self.caster.soulboundEffect)

    def canUse(self):
        return len(self.targets) == 1 and self.targets[0] != self.caster


#######################################
# Effects
#######################################
class SoulboundEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

    @classmethod
    def effectName(cls):
        return "Soulbound"

    @classmethod
    def effectEmoji(cls):
        return '👻'
