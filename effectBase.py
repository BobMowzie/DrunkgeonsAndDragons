from abc import ABC

class EffectBase(ABC):
  """A status effect base class"""
  def __init__(self, caster, target, turnsRemaining):
    self.caster = caster
    if caster:
      self.game = caster.game
    self.target = target
    self.turnsRemaining = turnsRemaining

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

  @classmethod
  def effectName(cls):
    return ''

  @classmethod
  def effectEmoji(self):
    return ''
