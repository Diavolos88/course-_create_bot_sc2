import time

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import UnitTypeId, AbilityId
from sc2.unit import Unit
from sc2.position import Point2
import random
from random import randint
class Pair:
    interation: int
    obj: Unit
    def __init__(self, obj, iteration):
        self.iteration = iteration
        self.obj = obj
class TerranBot(sc2.BotAI):
    barracks_with_reactor = []
    barracks_with_laboratory = []
    barracks_in_flight = []

    async def on_step(self, iteration: int):
        await self.distribute_workers()
        await self.build_scv()
        await self.build_supply()
        await self.expand()
        await self.buid_refinery()
        await self.offensive_force_buildings()

        await self.build_addons(iteration)
        await self.build_maradeuer()
        await self.build_marin()
        await self.attack()

    def find_target(self):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]
    async def attack(self):
        if self.units(UnitTypeId.MARINE).amount + self.units(UnitTypeId.MARAUDER).amount > 25:
            for unit in self.units(UnitTypeId.MARINE).idle:
                await self.do(unit.attack(self.find_target()))
            for unit in self.units(UnitTypeId.MARAUDER).idle:
                await self.do(unit.attack(self.find_target()))

        elif self.units(UnitTypeId.MARINE).amount + self.units(UnitTypeId.MARAUDER).amount > 4:
            if len(self.known_enemy_units) > 0:
                for unit in self.units(UnitTypeId.MARINE).idle:
                    await self.do(unit.attack(random.choice(self.known_enemy_units)))
                for unit in self.units(UnitTypeId.MARAUDER).idle:
                    await self.do(unit.attack(random.choice(self.known_enemy_units)))

    async def build_maradeuer(self):
        for barrack in self.units(UnitTypeId.BARRACKS).ready.idle:
            if barrack in self.barracks_with_laboratory:
                if self.can_afford(UnitTypeId.MARAUDER):
                    await self.do(barrack.train(UnitTypeId.MARAUDER))
    async def build_marin(self):
        for barrack in self.units(UnitTypeId.BARRACKS).ready.idle:
            if barrack in self.barracks_with_reactor:
                if self.can_afford(UnitTypeId.MARINE):
                    await self.do(barrack.train(UnitTypeId.MARINE))
                if self.can_afford(UnitTypeId.MARINE):
                    await self.do(barrack.train(UnitTypeId.MARINE))
    async def build_addons(self, iteration: int):
        addon = UnitTypeId.BARRACKSREACTOR if self.units(UnitTypeId.BARRACKSREACTOR).amount < 3 else UnitTypeId.BARRACKSTECHLAB
        for barrack in self.units(UnitTypeId.BARRACKS).ready.idle:
            if not barrack.has_add_on and self.can_afford(addon):
                await self.do(barrack.build(addon))
                self.barracks_with_laboratory.append(barrack) if addon is UnitTypeId.BARRACKSTECHLAB else self.barracks_with_reactor.append(barrack)
            if not barrack.has_add_on and self.can_afford(addon):
                self.barracks_in_flight.append(Pair(barrack, iteration))
                await self.do(barrack(AbilityId.LIFT_BARRACKS))
        pair: Pair
        for pair in self.barracks_in_flight:
            if pair.iteration == iteration or pair.iteration + 30 < iteration:
                if self.can_afford(addon):
                    new_location = Point2(pair.obj.position + (pair.obj.position * randint(1, 5) / 100).rounded)
                    await self.do(pair.obj(AbilityId.LAND_BARRACKS, new_location))
                    await self.do(pair.obj.build(addon))
                    if pair.obj.has_add_on:
                        self.barracks_in_flight.remove(pair)
                        self.barracks_with_laboratory.append(
                            pair.obj) if addon is UnitTypeId.BARRACKSTECHLAB else self.barracks_with_reactor.append(pair.obj)

    async def offensive_force_buildings(self):
        count_barracks = 4
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

