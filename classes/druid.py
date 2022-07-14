from copy import deepcopy

from base.playerBase import PlayerBase
from base.abilityBase import AbilityBase
from base.effectBase import EffectBase
from game.gameEvents import *


class Druid(PlayerBase):
    def __init__(self, user, game):
        PlayerBase.__init__(self, user, game)

    @classmethod
    def className(cls):
        return 'Druid'

    @classmethod
    def classEmoji(cls):
        return '🐾'

    @classmethod
    def classDescription(cls):
        return "Flexible class that can swap between offensive and defensive roles."

    def ability1(self):
        if self.hasEffect(WolfEffect):
            return Bite
        else:
            return Howl

    def ability2(self):
        if self.hasEffect(BearEffect):
            return Maul
        else:
            return EntanglingVines

    @classmethod
    def getInfo(cls):
        toPrint = "**" + cls.classEmoji() + " " + cls.className() + "**\n"
        toPrint += cls.classDescription() + "\n"
        druid = Druid(None, None)
        forms = {
            "Human": None,
            "Wolf": WolfEffect,
            "Bear": BearEffect
        }
        for name, effect in forms.items():
            separator = ""
            emoji = ""
            if effect:
                druid.activeEffects.clear()
                druid.activeEffects.append(effect(None, None, 1))
                emoji = " " + effect.effectEmoji()
                separator = "\* \* \* \* \* \* \* \* \* \* \* \*\n"
            toPrint += separator
            toPrint += "**" + name + " Form" + emoji + ":**\n"
            toPrint += "**Ability 1: " + druid.ability1().abilityName() + "**\n"
            toPrint += druid.ability1().abilityDescription() + "\n"
            toPrint += "**Ability 2: " + druid.ability2().abilityName() + "**\n"
            toPrint += druid.ability2().abilityDescription() + "\n"
        return toPrint


#######################################
# Abilities
#######################################
class Bite(AbilityBase):
    def __init__(self, caster: Druid, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseDealDamage, self.damageEffect, 0)

    @classmethod
    def abilityName(cls):
        return "Bite"

    @classmethod
    def abilityDescription(cls):
        return "Basic attack that deals 1 damage. Deals 3 damage if you are not targeted by any player this turn."

    def damageEffect(self, event):
        bonusDamage = 2
        for player in self.game.getPlayers():
            for action in player.getAllActiveAbilities():
                if action and self.caster in action.targets:
                    bonusDamage = 0
                    break
            if bonusDamage == 0:
                break
        self.caster.dealDamage(self.targets[0], 1 + bonusDamage)


class Howl(AbilityBase):
    def __init__(self, caster: Druid, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)
        self.subscribeEvent(PhasePostDamage, self.postEffect, 0)

    @classmethod
    def abilityName(cls):
        return "Howl"

    @classmethod
    def abilityDescription(cls):
        return "Switch to Wolf Form (🐺). Target gains Moonlit (🌙) next turn, making their attacks deal double damage."

    def applyEffects(self, event):
        self.caster.removeEffect(BearEffect)
        self.caster.addEffect(WolfEffect(self.caster, self.caster, 4))

    def postEffect(self, event):
        self.targets[0].removeEffect(MoonlitEffect)
        self.targets[0].addEffect(MoonlitEffect(self.caster, self.caster, 2))

    @classmethod
    def canSelfTarget(cls):
        return True


class Maul(AbilityBase):
    def __init__(self, caster: Druid, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseModifyActions, self.modifyActions, 0)
        self.subscribeEvent(PhaseDealDamage, self.damageEffect, 0)

    @classmethod
    def abilityName(cls):
        return "Maul"

    @classmethod
    def abilityDescription(cls):
        return "Target player uses their ability on you instead this turn. Deal damage to your target equal to the number of players who targetted you this turn."

    def modifyActions(self, event):
        target = self.targets[0]
        abilityCopy = deepcopy(target.activeAbility)
        abilityCopy.targets = [self.caster]
        target.modifiedAbilities.append(abilityCopy)
        target.activeAbility.canceled = True

    def damageEffect(self, event):
        targetCount = 0
        for player in self.caster.game.getPlayers():
            actions = player.modifiedAbilities
            for action in actions:
                if action and self.caster in action.targets:
                    targetCount += 1
                    break
        self.caster.dealDamage(self.targets[0], targetCount)


class EntanglingVines(AbilityBase):
    def __init__(self, caster: Druid, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)
        self.subscribeEvent(PhasePostDamage, self.postDamage, 0)

    @classmethod
    def abilityName(cls):
        return "Entangling Vines"

    @classmethod
    def abilityDescription(cls):
        return "Switch to Bear Form (🐻). Entangle (🌿) your target, causing them to skip their next turn."

    def postDamage(self, event):
        self.targets[0].removeEffect(EntangledEffect)
        self.targets[0].addEffect(EntangledEffect(self.caster, self.targets[0], 2))

    def applyEffects(self, event):
        self.caster.removeEffect(WolfEffect)
        self.caster.addEffect(BearEffect(self.caster, self.caster, 4))


#######################################
# Effects
#######################################
class WolfEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

    @classmethod
    def effectName(cls):
        return "Wolf"

    @classmethod
    def effectEmoji(cls):
        return '🐺'


class BearEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)

    @classmethod
    def effectName(cls):
        return "Bear"

    @classmethod
    def effectEmoji(cls):
        return '🐻'

    def applyEffects(self, event):
        self.target.takeDamageAddition = -1


class MoonlitEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)

    @classmethod
    def effectName(cls):
        return "Moonlit"

    @classmethod
    def effectEmoji(cls):
        return '🌙'

    def applyEffects(self, event):
        self.target.dealDamageMultiplier *= 2


class EntangledEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

        self.subscribeEvent(PhaseModifyActions, self.modifyActions, 0)

    @classmethod
    def effectName(cls):
        return "Entangled"

    @classmethod
    def effectEmoji(cls):
        return '🌿'

    def modifyActions(self, event):
        self.target.activeAbility.canceled = True
