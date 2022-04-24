from playerBase import PlayerBase
from abilityBase import AbilityBase
from effectBase import EffectBase


class Barbarian(PlayerBase):
    def __init__(self, user, game):
        PlayerBase.__init__(self, user, game)
        self.previousTarget = None
        self.consecutiveDamageBonus = 0

    @classmethod
    def className(cls):
        return 'Barbarian'

    @classmethod
    def classEmoji(cls):
        return '🪓'

    @classmethod
    def classDescription(cls):
        return "Bruiser and bully class. Purely offensive."

    @classmethod
    def ability1(self):
        return Strike

    @classmethod
    def ability2(self):
        return Enrage

    def skipTurn(self):
        self.previousTarget = None
        self.consecutiveDamageBonus = 0

    def resourceNumber(self):
        return self.consecutiveDamageBonus


#######################################
# Abilities
#######################################
class Strike(AbilityBase):
    def __init__(self, caster: Barbarian, targets):
        AbilityBase.__init__(self, caster, targets)

    @classmethod
    def abilityName(cls):
        return "Strike"

    @classmethod
    def abilityDescription(cls):
        return "Basic attack. Gets stronger with consecutive hits on an opponent."

    def damageEffect(self):
        target = self.targets[0]

        if self.caster.previousTarget != target:
            self.caster.previousTarget = target
            self.caster.consecutiveDamageBonus = 0

        self.caster.dealDamage(target, 1 + self.caster.consecutiveDamageBonus)

    def postEffect(self):
        damageDealt = self.caster.damageDealt.get(self.caster.previousTarget)
        if damageDealt and damageDealt > 0:
            self.caster.consecutiveDamageBonus = min(
                self.caster.consecutiveDamageBonus + 1, 2)
        else:
            self.caster.previousTarget = None

    def canUse(self):
        return len(self.targets) == 1 and self.targets[0] != self.caster


class Enrage(AbilityBase):
    def __init__(self, caster: Barbarian, targets):
        AbilityBase.__init__(self, caster, targets)
        self.targets = [self.caster]

    @classmethod
    def abilityName(cls):
        return "Enrage"

    @classmethod
    def abilityDescription(cls):
        return "Deal double damage for the following 3 turns. Using this will not reset consecutive target hits."

    def postEffect(self):
        self.targets[0].removeEffect(EnrageEffect)
        self.targets[0].addEffect(EnrageEffect(self.caster, self.caster, 4))

    def canUse(self):
        return len(self.targets) == 1 and self.targets[0] == self.caster


#######################################
# Effects
#######################################
class EnrageEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

    @classmethod
    def effectName(cls):
        return "Enrage"

    @classmethod
    def effectEmoji(self):
        return '💢'

    def applyEffects(self):
        self.target.attackMultiplier *= 2
