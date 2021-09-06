from enum import Enum
from commons.skills import *
from commons.utils import *


class Target(Enum):
    ClosestToPlayer = 0
    LowestHealth = 1
    MostFed = 2


class TargetingConfig:
    targets = [Target.ClosestToPlayer, Target.LowestHealth, Target.MostFed]
    targeting_lambdas = {
        Target.ClosestToPlayer: (lambda player, enemy: player.pos.distance(enemy.pos)),
        Target.LowestHealth: (lambda player, enemy: enemy.health),
        Target.MostFed: (
            lambda player, enemy: -sum([item.cost for item in enemy.items])
        ),
    }
    selected = 0
    target_minions = False
    target_jungle = False
    target_turret = False
    target_others = False

    def draw(self, ui):
        ui.separator()
        self.selected = ui.listbox(
            "Target", [str(target)[7:] for target in self.targets], self.selected
        )
        self.target_jungle = ui.checkbox(
            "Allow targeting jungle monsters", self.target_jungle
        )
        self.target_minions = ui.checkbox(
            "Allow targeting minions", self.target_minions
        )
        self.target_turret = ui.checkbox("Allow targeting turrets", self.target_turret)
        self.target_others = ui.checkbox("Allow targeting others", self.target_others)

    def get_target(self, game, range):
        player = game.player

        target_info = self.targets[self.selected]
        target = self.find_target(
            game, game.champs, range, self.targeting_lambdas[target_info]
        )
        if not target:
            typedamage = self.targeting_lambdas[target_info]
            others = []
            if self.target_turret:
                others.extend(game.turrets)
            if self.target_jungle:
                others.extend(game.jungle)
            if self.target_others:
                others.extend(game.others)

            if len(others) > 0:
                target = self.find_target(game, others, range, typedamage)

        return target

    def get_laneclear(self, game, range):
        player = game.player

        target_info = self.targets[self.selected]
        target = self.find_target(
            game, game.champs, range, self.targeting_lambdas[target_info]
        )
        if not target:
            typedamage = self.targeting_lambdas[target_info]
            others = []
            if self.target_turret:
                others.extend(game.turrets)
            if self.target_jungle:
                others.extend(game.jungle)
            if self.target_others:
                others.extend(game.others)
            if self.target_minions:
                others.extend(game.minions)

            if len(others) > 0:
                target = self.find_target(game, others, range, typedamage)

        return target

    def find_target(self, game, array, range, value_extractor):
        self = game.player
        champ_healt = self.health
        target = None
        min = 99999999
        for obj in array:

            if (
                not obj.is_alive
                or not obj.is_visible
                or not obj.isTargetable
                or obj.is_ally_to(game.player)
                or (
                    game.distance(game.player, obj)
                    - game.player.gameplay_radius
                    - obj.gameplay_radius
                )
                > range
            ):
                continue
            val = value_extractor(game.player, obj)
            if val < min:
                min = val
                target = obj

        return target

    def load_from_cfg(self, cfg):
        self.selected = cfg.get_int("targeting_target", 0)
        self.target_jungle = cfg.get_bool("target_jungle", False)
        self.target_minions = cfg.get_bool("target_minions", False)
        self.target_turret = cfg.get_bool("target_turret", False)
        self.target_others = cfg.get_bool("target_others", False)

    def save_to_cfg(self, cfg):
        cfg.set_int("targeting_target", self.selected)
        cfg.set_bool("target_jungle", self.target_jungle)
        cfg.set_bool("target_minions", self.target_minions)
        cfg.set_bool("target_turret", self.target_turret)
        cfg.set_bool("target_others", self.target_others)
