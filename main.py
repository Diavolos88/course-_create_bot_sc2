import time

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import UnitTypeId

class TerranBot(sc2.BotAI):
    async def on_step(self, iteration: int):
        await self.distribute_workers()
        await self.build_scv()
        await self.build_supply()

    async def build_scv(self):
        for cc in self.units(UnitTypeId.COMMANDCENTER).ready.noqueue:
            if self.can_afford(UnitTypeId.SCV):
                await self.do(cc.train(UnitTypeId.SCV))

    async def build_supply(self):
        if self.supply_left < 5 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
            cc = self.units(UnitTypeId.COMMANDCENTER).ready
            if cc.exists:
                if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                    await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.first)


if __name__ == '__main__':
    run_game(maps.get("AbyssalReefLE"),[
        Bot(Race.Terran, TerranBot()),
        Computer(Race.Terran, Difficulty.Easy)
    ], realtime=True)

