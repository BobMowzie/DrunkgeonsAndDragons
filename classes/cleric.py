from playerBase import PlayerBase
from abilityBase import AbilityBase
from effectBase import EffectBase

class Cleric(PlayerBase):
  def __init__(self, user, game):
    PlayerBase.__init__(self, user, game)
    self.blessings = 1

  @classmethod
  def className(cls):
    return 'Cleric'

  @classmethod
  def classEmoji(cls):
    return '📖'
  
  @classmethod
  def classDescription(cls):
    return "Support class. Purely defensive."

  @classmethod
  def ability1(self):
    return Cure

  @classmethod
  def ability2(self):
    return DivineBarrier

  def resourceNumber(self):
    return self.blessings

#######################################
# Abilities
#######################################
class Cure(AbilityBase):
  def __init__(self, caster: Cleric, targets):
    AbilityBase.__init__(self, caster, targets)

  @classmethod
  def abilityName(cls):
    return "Cure"

  @classmethod
  def abilityDescription(cls):
    return "Clear all status effects from a target and prevent the target from receiving any new status effects this turn. Each effect cured grants one blessing to the Cleric."

  def startTurnEffect(self):
    target = self.targets[0]
    target.curingClerics.append(self.caster)

  def canUse(self):
    return len(self.targets) == 1

class DivineBarrier(AbilityBase):
  def __init__(self, caster: Cleric, targets):
    AbilityBase.__init__(self, caster, targets)

  @classmethod
  def abilityName(cls):
    return "Divine Barrier"

  @classmethod
  def abilityDescription(cls):
    return "Expend all blessings to create a barrier on a target. For however many blessings spent, the barrier blocks that many hits of damage."
  
  def applyEffects(self):
    target = self.targets[0]
    target.addEffect(DivineBarrierEffect(self.caster, target, self.caster.blessings))
    self.caster.blessings = 1

  def canUse(self):
    return len(self.targets) == 1

#######################################
# Effects
#######################################
class DivineBarrierEffect(EffectBase):
  def __init__(self, caster, target, turnsRemaining):
    EffectBase.__init__(self, caster, target, turnsRemaining)

  @classmethod
  def effectName(cls):
    return "Divine Barrier"

  @classmethod
  def effectEmoji(self):
    return '✝️'
