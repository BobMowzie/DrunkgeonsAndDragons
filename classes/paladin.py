from playerBase import PlayerBase
from abilityBase import AbilityBase
from effectBase import EffectBase
import math

class Paladin(PlayerBase):  
  def __init__(self, user, game):
    PlayerBase.__init__(self, user, game)
    self.biggestAttack = 0
    self.biggestAttackLastTurn = 0
  
  @classmethod
  def className(cls):
    return 'Knight'
  
  @classmethod
  def classDescription(cls):
    return 'Tank class. Turns defense into offense.'

  @classmethod
  def ability1(self):
    return Shield

  @classmethod
  def ability2(self):
    return Retribution

  @classmethod
  def classEmoji(cls):
    return '⚔️'

  def resourceNumber(self):
    return 1 + self.biggestAttackLastTurn

  def takeDamage(self):
    PlayerBase.takeDamage(self)
    for player, amount in self.damageTaken:
      amount = math.floor(amount * self.takeDamageMultiplier)
      if amount > self.biggestAttack:
        self.biggestAttack = amount

  def endTurn(self):
    PlayerBase.endTurn(self)
    self.biggestAttackLastTurn = self.biggestAttack
    self.biggestAttack = 0

#######################################
# Abilities
#######################################
class Shield(AbilityBase):
  def __init__(self, caster: Paladin, targets):
    AbilityBase.__init__(self, caster, targets)

  @classmethod
  def abilityName(cls):
    return "Shield"

  @classmethod
  def abilityDescription(cls):
    return "Redirect all incoming damage on a target player onto you. That damage is halved (rounded down)."
  
  def applyEffects(self):
    target = self.targets[0]
    target.addEffect(ShieldEffect(self.caster, target, 1))

  def canUse(self):
    return len(self.targets) == 1

class Retribution(AbilityBase):
  def __init__(self, caster: Paladin, targets):
    AbilityBase.__init__(self, caster, targets)

  @classmethod
  def abilityName(cls):
    return "Retribution"
  
  @classmethod
  def abilityDescription(cls):
    return "Deal damage to a target equal to the largest single hit of damage you took or blocked last turn, plus 1."
  
  def damageEffect(self):
    target = self.targets[0]   
    self.caster.dealDamage(target, self.caster.biggestAttackLastTurn + 1)

  def canUse(self):
    return len(self.targets) == 1 and self.targets[0] != self.caster

#######################################
# Effects
#######################################
class ShieldEffect(EffectBase):
  def __init__(self, caster, target, turnsRemaining):
    EffectBase.__init__(self, caster, target, turnsRemaining)

  @classmethod
  def effectName(cls):
    return "Shield"

  @classmethod
  def effectEmoji(self):
    return '🛡️'
