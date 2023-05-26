import time

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import UnitTypeId

class TerranBot(sc2.BotAI):
    barracks_with_reactor = []
    barracks_with_laboratory = []

    async def on_step(self, iteration: int):
        await self.distribute_workers()
        await self.build_scv()
        await self.build_supply()
        await self.expand()
        await self.buid_refinery()
        await self.offensive_force_buildings()
        await self.build_army()

    async def build_army(self):
        for barrack in self.units(UnitTypeId.BARRACKS).ready.idle:
            if not barrack.has_add_on:
                if self.can_afford(UnitTypeId.BARRACKSREACTOR) and self.units(UnitTypeId.BARRACKSREACTOR).amount < 2:
                    self.barracks_with_reactor.append(barrack)
                    await self.do(barrack.build(UnitTypeId.BARRACKSREACTOR))
                else:
                    self.barracks_with_laboratory.append(barrack)
                    await self.do(barrack.build(UnitTypeId.BARRACKSTECHLAB))

        for barrack in self.units(UnitTypeId.BARRACKS).ready.idle:
            if barrack in self.barracks_with_reactor:
                if self.can_afford(UnitTypeId.MARINE):
                    await self.do(barrack.train(UnitTypeId.MARINE))
                if self.can_afford(UnitTypeId.MARINE):
                    await self.do(barrack.train(UnitTypeId.MARINE))
            elif barrack in self.barracks_with_laboratory:
                if self.can_afford(UnitTypeId.MARAUDER):
                    await self.do(barrack.train(UnitTypeId.MARAUDER))

    async def offensive_force_buildings(self):
        count_barracks = 3
        if self.units(UnitTypeId.COMMANDCENTER).amount == 1:
            count_barracks = 1
        if self.units(UnitTypeId.BARRACKS).amount < count_barracks:
            if self.can_afford(UnitTypeId.BARRACKS):
                cc = self.units(UnitTypeId.COMMANDCENTER).ready
                if cc.exists:
                    await self.build(UnitTypeId.BARRACKS, near=cc.random.position.towards(self.game_info.map_center, 5))


    async def buid_refinery(self):
        if self.can_afford(UnitTypeId.REFINERY):
            for cc in self.units(UnitTypeId.COMMANDCENTER).ready:
                vespenes = self.state.vespene_geyser.closer_than(15.0, cc)
                for vespen in vespenes:
                    worker = self.select_build_worker(vespen.position)
                    if worker is not None and not self.units(UnitTypeId.REFINERY).closer_than(1.0, vespen).exists:
                        await self.do(worker.build(UnitTypeId.REFINERY, vespen))

    async def expand(self):
        if self.units(UnitTypeId.COMMANDCENTER).amount < 2 and self.can_afford(UnitTypeId.COMMANDCENTER):
            await self.expand_now()


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
    ], realtime=False)

