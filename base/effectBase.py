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

    @classmethod
    def effectName(cls):
        return ''

    @classmethod
    def effectEmoji(cls):
        return ''
