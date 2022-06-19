from base.playerBase import PlayerBase
from base.abilityBase import AbilityBase
from base.effectBase import EffectBase

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
  def getInfo(self):
    toPrint = "**" + self.classEmoji() + " " + self.className() + "**\n"
    toPrint += self.classDescription() + "\n"
    druid = Druid(None, None)
    forms = {
      "Human": None,
      "Wolf": WolfEffect,
      "Bear": BearEffect
    }
    for name, effect in forms.items():
      if effect:
        druid.activeEffects.clear()
        druid.activeEffects.append(effect(None, None, 1))
      toPrint += "**" + name + " Form:**\n"
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
  
  @classmethod
  def abilityName(cls):
    return "Bite"
  
  @classmethod
  def abilityDescription(cls):
    return "Basic attack that deals 1 damage. Deals 3 damage if you are not targeted by any player this turn."

  def damageEffect(self):
    bonusDamage = 2
    for action in self.caster.game.actions.values():
      if action and self.caster in action.targets:
        bonusDamage = 0
        break
    self.caster.dealDamage(self.targets[0], 1 + bonusDamage)

  def canUse(self):
    return len(self.targets) == 1 and self.targets[0] != self.caster

class Howl(AbilityBase):
  def __init__(self, caster: Druid, targets):
    AbilityBase.__init__(self, caster, targets)

  @classmethod
  def abilityName(cls):
    return "Howl"
  
  @classmethod
  def abilityDescription(cls):
    return "Switch to wolf form. Target deals double damage next turn."
  
  def applyEffects(self):
    self.caster.removeEffect(BearEffect)
    self.caster.addEffect(WolfEffect(self.caster, self.caster, 4))

  def postEffect(self):
    self.targets[0].removeEffect(MoonlitEffect)
    self.targets[0].addEffect(MoonlitEffect(self.caster, self.caster, 2))

  def canUse(self):
    return len(self.targets) == 1

class Maul(AbilityBase):
  def __init__(self, caster: Druid, targets):
    AbilityBase.__init__(self, caster, targets)
  
  @classmethod
  def abilityName(cls):
    return "Maul"
  
  @classmethod
  def abilityDescription(cls):
    return "Target player uses their ability on you instead this turn. Deal damage to your target equal to the number of players who targetted you this turn."

  def modifyActions(self):
    action = self.caster.game.modifiedActions.get(self.targets[0])
    if action:
      for i in range(len(action.targets)):
        action.targets[i] = self.caster

  def damageEffect(self):
    targetCount = 0
    for action in self.caster.game.actions.values():
      if action and self.caster in action.targets:
        targetCount += 1
    self.caster.dealDamage(self.targets[0], targetCount)

  def canUse(self):
    return len(self.targets) == 1 and self.targets[0] != self.caster

class EntanglingVines(AbilityBase):
  def __init__(self, caster: Druid, targets):
    AbilityBase.__init__(self, caster, targets)

  @classmethod
  def abilityName(cls):
    return "Entangling Vines"
  
  @classmethod
  def abilityDescription(cls):
    return "Switch to bear form. Target skips their turn."
  
  def startTurnEffect(self):
    self.targets[0].removeEffect(EntangledEffect)
    self.targets[0].addEffect(EntangledEffect(self.caster, self.targets[0], 1))

  def applyEffects(self):
    self.caster.removeEffect(WolfEffect)
    self.caster.addEffect(BearEffect(self.caster, self.caster, 4))

  def canUse(self):
    return len(self.targets) == 1 and self.targets[0] != self.caster

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
  def effectEmoji(self):
    return '🐺'

class BearEffect(EffectBase):
  def __init__(self, caster, target, turnsRemaining):
    EffectBase.__init__(self, caster, target, turnsRemaining)

  @classmethod
  def effectName(cls):
    return "Bear"
    
  @classmethod
  def effectEmoji(self):
    return '🐻'

  def applyEffects(self):
    self.target.takeDamageAddition = 1

class MoonlitEffect(EffectBase):
  def __init__(self, caster, target, turnsRemaining):
    EffectBase.__init__(self, caster, target, turnsRemaining)

  @classmethod
  def effectName(cls):
    return "Moonlit"
    
  @classmethod
  def effectEmoji(self):
    return '🌙'

  def applyEffects(self):
    self.target.dealDamageMultiplier *= 2

class EntangledEffect(EffectBase):
  def __init__(self, caster, target, turnsRemaining):
    EffectBase.__init__(self, caster, target, turnsRemaining)

  @classmethod
  def effectName(cls):
    return "Entangled"
    
  @classmethod
  def effectEmoji(self):
    return '🌿'

  def modifyActions(self):
    self.caster.game.modifiedActions[self.target] = None
