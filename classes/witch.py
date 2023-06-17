from base.playerBase import PlayerBase
from base.abilityBase import AbilityBase
from base.effectBase import EffectBase
from game.gameEvents import *


class Witch(PlayerBase):
    def __init__(self, user, game):
        PlayerBase.__init__(self, user, game)

    @classmethod
    def className(cls):
        return 'Witch'

    @classmethod
    def classEmoji(cls):
        return '🧹'

    @classmethod
    def classDescription(cls):
        return "Offensive disabler class that can prevent abilities and status effects while dealing damage. "

    @classmethod
    def ability1(cls):
        return Potion

    @classmethod
    def ability2(cls):
        return Hex


#######################################
# Abilities
#######################################
class Potion(AbilityBase):
    def __init__(self, caster: Witch, targets):
        AbilityBase.__init__(self, caster, targets)
        self.damageDealt = 0

        self.subscribeEvent(PhaseDealDamage, self.damageEffect, 0)
        self.subscribeEvent(PhaseStartTurns, self.countEffects, -99)
        self.subscribeEvent(PhaseStartTurns, self.removeEffects, -98)
        self.subscribeEvent(EventApplyEffect, self.applyEffectsEvent, 0)

    @classmethod
    def abilityName(cls):
        return "Potion"

    @classmethod
    def abilityDescription(cls):
        return 'Clear all status effects from a target. Deal 1 damage to the target, plus 2 damage for each status effect cleared.'

    def countEffects(self, event):
        target = self.targets[0]
        self.damageDealt += 1 + len(target.activeEffects) * 2

    def removeEffects(self, event):
        target = self.targets[0]
        target.activeEffects.clear()

    def applyEffectsEvent(self, event):
        target = self.targets[0]
        if event.target == target:
            event.newCanceled = True
            self.damageDealt += 2

    def damageEffect(self, event):
        target = self.targets[0]
        self.caster.dealDamage(target, self.damageDealt, self)

    def actionText(self):
        return f"clearing all of their status effects and dealing {self.damageDealt} damage"


class Hex(AbilityBase):
    def __init__(self, caster: Witch, targets):
        AbilityBase.__init__(self, caster, targets)

        self.numTurns = 0

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)

    @classmethod
    def abilityName(cls):
        return "Hex"

    @classmethod
    def abilityDescription(cls):
        return 'Hex (🐸) your target and yourself for the next 2 turns, preventing both of you from using Ability 2.'

    def applyEffects(self, event):
        target = self.targets[0]
        target.addEffect(HexEffect(self.caster, target, 2))
        self.caster.addEffect(HexEffect(self.caster, target, 2))

    def actionText(self):
        return "hexing (🐸) them both for 2 turns and blocking Ability 2"


#######################################
# Effects
#######################################
class HexEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

        self.subscribeEvent(PhaseModifyActions, self.modifyActions, -98)

    @classmethod
    def effectName(cls):
        return "Hex"

    @classmethod
    def effectEmoji(cls):
        return '🐸'

    def modifyActions(self, event):
        for player in self.game.players.values():
            if player.activeAbility:
                if isinstance(player.activeAbility, player.ability2()):
                    newAbilityClass = player.ability1()
                    newAbility = newAbilityClass(player, player.activeAbility.targets)
                    newAbility.canceled = player.activeAbility.canceled
                    player.activeAbility = newAbility
