import random


class DebugUser:

    def __init__(self, game, name):
        super().__init__()
        self.game = game
        self.name = name

    async def addToGame(self):
        from base.playerBase import classNames
        await self.game.addPlayer(self, random.choice(list(classNames.values())))

    async def chooseAbility(self):
        await self.game.enterAction(self, random.randint(1, 2), [random.choice(list(self.game.players.keys()))])
