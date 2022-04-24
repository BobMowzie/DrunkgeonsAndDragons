from abc import ABC

class AbilityBase(ABC):
  """A player ability base class"""
  def __init__(self, caster, targets):
    self.caster = caster
    self.game = caster.game
    self.targets = targets

  def startTurnEffect(self):
    pass

  def modifyActions(self):
    pass

  def applyEffects(self):
    pass

  def preDamageEffect(self):
    pass

  def damageEffect(self):
    pass

  def postEffect(self):
    pass

  def canUse(self):
    True

  @classmethod
  def abilityName(cls):
    return ''

  @classmethod
  def abilityDescription(cls):
    return ''
