class DamageInstance:
    def __init__(self, attacker, target, amount, source=None):
        self.attacker = attacker
        self.source = source

        self.originalTarget = target
        self.target = target
        self.newTarget = target

        self.originalAmount = amount
        self.amount = amount
        self.newAmount = amount

        self.canceled = False
        self.newCanceled = False

    def update(self):
        self.amount = self.newAmount
        self.canceled = self.newCanceled
        self.target = self.newTarget
