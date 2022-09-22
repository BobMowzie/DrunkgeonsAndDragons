from game.gameEvents import EventSubscriber


class EffectBase(EventSubscriber):
    """A status effect base class"""

    def __init__(self, caster, target, turnsRemaining):
        super().__init__()
        self.caster = caster
        if caster:
            self.game = caster.game
        self.target = target
        self.turnsRemaining = turnsRemaining
        self.timed = True
        self.hasTurnsRemaining = True

    @classmethod
    def effectName(cls):
        return ''

    @classmethod
    def effectEmoji(cls):
        return ''

    def decrementTurnsRemaining(self):
        if self.timed:
            self.turnsRemaining = max(self.turnsRemaining - 1, 0)
