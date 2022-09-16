from game.gameEvents import EventSubscriber


class AbilityBase(EventSubscriber):
    """A player ability base class"""

    def __init__(self, caster, targets):
        super().__init__()
        self.caster = caster
        self.game = caster.game
        self.targets = targets
        self.canceled = False

    @classmethod
    def abilityName(cls):
        return ''

    @classmethod
    def abilityDescription(cls):
        return ''

    def canUse(self):
        numTargets = len(self.targets)
        if numTargets > self.maxNumTargets():
            return False, "Too many targets for ability **" + self.abilityName()\
                   + "**. Given " + str(numTargets) + ", maximum is " + str(self.maxNumTargets()) + "."
        if numTargets < self.minNumTargets():
            return False, "Too few targets for ability **" + self.abilityName()\
                   + "**. Given " + str(numTargets) + ", minimum is " + str(self.minNumTargets()) + "."
        if not self.canSelfTarget():
            if self.caster in self.targets:
                return False, "Cannot target self with ability **" + self.abilityName() + "**."
        if not self.canTargetOthers():
            if self.caster not in self.targets:
                return False, "Must target self with ability **" + self.abilityName() + "**."
        return True, ""

    @classmethod
    def canSelfTarget(cls):
        return False

    @classmethod
    def canTargetOthers(cls):
        return True

    @classmethod
    def maxNumTargets(cls):
        return 1

    @classmethod
    def minNumTargets(cls):
        return 1
