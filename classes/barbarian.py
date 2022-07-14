from base.playerBase import PlayerBase
from base.abilityBase import AbilityBase
from base.effectBase import EffectBase
from game.gameEvents import *


class Barbarian(PlayerBase):
    def __init__(self, user, game):
        PlayerBase.__init__(self, user, game)
        self.previousTarget = None
        self.consecutiveDamageBonus = 0

        self.subscribeEvent(PhaseStartTurns, self.startTurnEvent, 0)

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
    def ability1(cls):
        return Strike

    @classmethod
    def ability2(cls):
        return Enrage

    def startTurnEvent(self, event):
        if not self.activeAbility:
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

        self.subscribeEvent(PhaseDealDamage, self.damageEffect, 0)
        self.subscribeEvent(PhasePostDamage, self.postEffect, 0)

    @classmethod
    def abilityName(cls):
        return "Strike"

    @classmethod
    def abilityDescription(cls):
        return "Basic attack for 1 damage. Gets stronger by 1 damage with consecutive hits on an opponent, dealing a maximum of 3 damage."

    def damageEffect(self, event):
        target = self.targets[0]

        if self.caster.previousTarget != target:
            self.caster.previousTarget = target
            self.caster.consecutiveDamageBonus = 0

        self.caster.dealDamage(target, 1 + self.caster.consecutiveDamageBonus, self)

    def postEffect(self, event):
        consecutiveHit = False
        for damageInstance in self.caster.previousTarget.damageTaken:
            if damageInstance.attacker == self.caster and damageInstance.amount > 0 and not damageInstance.canceled:
                consecutiveHit = True
                break

        if consecutiveHit:
            self.caster.consecutiveDamageBonus = min(self.caster.consecutiveDamageBonus + 1, 2)
        else:
            self.caster.consecutiveDamageBonus = 0
            self.caster.previousTarget = None


class Enrage(AbilityBase):
    def __init__(self, caster: Barbarian, targets):
        AbilityBase.__init__(self, caster, targets)
        if len(self.targets) == 0:
            self.targets = [self.caster]

        self.subscribeEvent(PhasePostDamage, self.postEffect, 0)

    @classmethod
    def abilityName(cls):
        return "Enrage"

    @classmethod
    def abilityDescription(cls):
        return "Enrage (💢) yourself to deal double damage for the following 3 turns. Using this will not reset consecutive target hits from Strike."

    def postEffect(self, event):
        self.targets[0].removeEffect(EnrageEffect)
        self.targets[0].addEffect(EnrageEffect(self.caster, self.caster, 4))

    @classmethod
    def canTargetOthers(cls):
        return False

    @classmethod
    def minNumTargets(cls):
        return 0


#######################################
# Effects
#######################################
class EnrageEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)

    @classmethod
    def effectName(cls):
        return "Enrage"

    @classmethod
    def effectEmoji(cls):
        return '💢'

    def applyEffects(self, event):
        self.target.dealDamageMultiplier *= 2
