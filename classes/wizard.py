from playerBase import PlayerBase
from abilityBase import AbilityBase
from effectBase import EffectBase

class Wizard(PlayerBase):
  def __init__(self, user, game):
    PlayerBase.__init__(self, user, game)
    self.power = 1

  @classmethod
  def className(cls):
    return 'Wizard'

  @classmethod
  def classEmoji(cls):
    return '🪄'
  
  @classmethod
  def classDescription(cls):
    return "Offensive but fragile class that charges up power by skipping turns and unleashes it in powerful spells. Power resets to 1 if they take damage."

  @classmethod
  def ability1(self):
    return Fireball

  @classmethod
  def ability2(self):
    return Incinerate

  def skipTurn(self):
    if self.damageTakenThisTurn == 0:
      self.power += 2
    else:
      self.power = 1

  def endTurn(self):
    if self.damageTakenThisTurn > 0:
      self.power = 1
    PlayerBase.endTurn(self)

  def resourceNumber(self):
    return self.power

#######################################
# Abilities
#######################################
class Fireball(AbilityBase):
  def __init__(self, caster: Wizard, targets):
    AbilityBase.__init__(self, caster, targets)
  
  @classmethod
  def abilityName(cls):
    return "Fireball"
  
  @classmethod
  def abilityDescription(cls):
    return 'Spend all your power to deal that much damage to a target.'

  def damageEffect(self):
    target = self.targets[0]
    self.caster.dealDamage(target, self.caster.power)
    self.caster.power = 1

  def canUse(self):
    return len(self.targets) == 1 and self.targets[0] != self.caster

class Incinerate(AbilityBase):
  def __init__(self, caster: Wizard, targets):
    AbilityBase.__init__(self, caster, targets)

  @classmethod
  def abilityName(cls):
    return "Incinerate"
  
  @classmethod
  def abilityDescription(cls):
    return 'Spend all your power to burn your target for that many turns.'
  
  def applyEffects(self):
    target = self.targets[0]   
    target.addEffect(BurnEffect(self.caster, target, self.caster.power))
    self.caster.power = 1

  def canUse(self):
    return len(self.targets) == 1 and self.targets[0] != self.caster

#######################################
# Effects
#######################################
class BurnEffect(EffectBase):
  def __init__(self, caster, target, turnsRemaining):
    EffectBase.__init__(self, caster, target, turnsRemaining)

  def damageEffect(self):
    self.caster.dealDamage(self.target, 1)

  @classmethod
  def effectName(cls):
    return "Burn"

  @classmethod
  def effectEmoji(self):
    return '🔥'