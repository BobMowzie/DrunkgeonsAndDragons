from game.gameEvents import EventSubscriber


class AbilityBase(EventSubscriber):
    """A player ability base class"""

    def __init__(self, caster, targets):
        super().__init__()
        self.caster = caster
        self.game = caster.game
        self.targets = targets
        self.canceled = False

    def canUse(self):
        return True

    @classmethod
    def abilityName(cls):
        return ''

    @classmethod
    def abilityDescription(cls):
        return ''
