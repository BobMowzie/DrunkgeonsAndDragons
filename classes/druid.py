from copy import deepcopy

from base.playerBase import PlayerBase
from base.abilityBase import AbilityBase
from base.effectBase import EffectBase
from game.gameEvents import *


class Druid(PlayerBase):
    def __init__(self, user, game):
        PlayerBase.__init__(self, user, game)
        self.targetedByCount = 0

        self.subscribeEvent(PhaseEndTurns, self.endTurns, 0)

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
            return EntanglingVines

    def ability2(self):
        if self.hasEffect(BearEffect):
            return Maul
        else:
            return Thornskin

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

    def endTurns(self):
        self.targetedByCount = 0
        for player in self.game.getPlayers():
            for action in player.getAllActiveAbilities():
                if action and self in action.targets:
                    self.targetedByCount += 1


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
        return "Basic attack that deals 1 damage. Deals 3 damage if you are not targeted by any player last turn."

    def damageEffect(self, event):
        bonusDamage = 0
        if self.caster.targetedByCount == 0:
            bonusDamage = 2
        self.caster.dealDamage(self.targets[0], 1 + bonusDamage)


class EntanglingVines(AbilityBase):
    def __init__(self, caster: Druid, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhasePostDamage, self.postDamage, 0)

    @classmethod
    def abilityName(cls):
        return "Entangling Vines"

    @classmethod
    def abilityDescription(cls):
        return "Switch to Wolf Form (🐺). Entangle (🌿) your target, causing them to skip their next turn."

    def postDamage(self, event):
        self.targets[0].removeEffect(EntangledEffect)
        self.targets[0].addEffect(EntangledEffect(self.caster, self.targets[0], 2))


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
        return "Target player uses their ability on you instead this turn. Deal damage to your target equal to the number of players who targetted you last turn."

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


class Thornskin(AbilityBase):
    def __init__(self, caster: Druid, targets):
        AbilityBase.__init__(self, caster, targets)

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)

    @classmethod
    def abilityName(cls):
        return "Thornskin"

    @classmethod
    def abilityDescription(cls):
        return "Switch to Bear Form (🐻). Grow thorns (🌵) on your target, causing any players who target them to take 1 damage."

    def applyEffects(self, event):
        self.targets[0].removeEffect(ThornskinEffect)
        self.targets[0].addEffect(ThornskinEffect(self.caster, self.targets[0], 2))
        self.caster.removeEffect(WolfEffect)
        self.caster.addEffect(BearEffect(self.caster, self.caster, 4))

    @classmethod
    def canSelfTarget(cls):
        return True


#######################################
# Effects
#######################################
class WolfEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

        self.subscribeEvent(PhaseApplyEffects, self.applyEffects, 0)

    @classmethod
    def effectName(cls):
        return "Wolf"

    @classmethod
    def effectEmoji(cls):
        return '🐺'

    def applyEffects(self, event):
        self.target.takeDamageAddition += 1


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
        self.target.takeDamageAddition += -1

class ThornskinEffect(EffectBase):
    def __init__(self, caster, target, turnsRemaining):
        EffectBase.__init__(self, caster, target, turnsRemaining)

        self.subscribeEvent(PhaseDealDamage, self.dealDamage, 0)

    @classmethod
    def effectName(cls):
        return "Thornskin"

    @classmethod
    def effectEmoji(cls):
        return '🌵'

    def dealDamage(self, event):
        for player in self.game.getPlayers():
            for action in player.getAllActiveAbilities():
                if action and self.caster in action.targets:
                    self.caster.dealDamage(player, 1, self)

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
