from lview import *
from commons.targeting import *
from commons.targeting import TargetingConfig
from commons.api import *
import json, random
from time import time

show_healable = False
auto_qss = True
heal_percent = 0
auto_heal = True
auto_barrier = True
targeting = TargetingConfig()
lview_script_info = {
    "script": "Activator",
    "author": "bckd00r",
    "description": "Activator",
}


def lview_load_cfg(cfg):
    global auto_heal, heal_percent
    global auto_qss
    auto_qss = cfg.get_bool("Auto QSS", True)
    heal_percent = cfg.get_float("heal_percent", 20)
    auto_heal = cfg.get_bool("auto_heal", True)
    auto_barrier = cfg.get_bool("auto_barrier", True)


def lview_save_cfg(cfg):
    global auto_heal, heal_percent
    cfg.set_float("heal_percent", heal_percent)
    cfg.set_bool("auto_heal", auto_heal)
    cfg.set_bool("auto_barrier", auto_barrier)


def lview_draw_settings(game, ui):
    global auto_heal, heal_percent, auto_barrier

    ui.begin("WS+ Activator")
    if ui.treenode("Heal"):
        auto_heal = ui.checkbox("Enabled", auto_heal)
        heal_percent = ui.sliderfloat("Auto heal percent %", heal_percent, 1, 100)
        ui.treepop()
    if ui.treenode("Barrier"):
        auto_barrier = ui.checkbox("Enabled", auto_barrier)
        heal_percent = ui.sliderfloat("Auto heal percent %", heal_percent, 1, 100)
        ui.treepop()
    ui.end()


def AutoHeal(game):
    global heal_percent
    heal = game.player.get_summoner_spell(SummonerSpellType.Heal)
    if heal == None:
        return
    hp = int(game.player.health / game.player.max_health * 100)
    if hp < heal_percent and heal.get_current_cooldown(game.time) == 0.0:
        heal.trigger()


def AutoBarrier(game):
    global heal_percent
    barrier = game.player.get_summoner_spell(SummonerSpellType.Barrier)
    if barrier == None:
        return
    hp = int(game.player.health / game.player.max_health * 100)
    if hp < heal_percent and barrier.get_current_cooldown(game.time) == 0.0:
        barrier.trigger()


def GetBestTargetsInRange(game, atk_range=0):
    num = 10000
    if atk_range == 0:
        atk_range = game.player.atkRange
    for champ in game.champs:
        if (
            champ
            and champ.is_visible
            and champ.is_enemy_to(game.player)
            and champ.isTargetable
            and champ.is_alive
            and game.distance(game.player, champ) <= atk_range
        ):
            if is_last_hitable(game, game.player, champ):
                return champ
            elif champ.health <= num:
                num = champ.health
                return champ
            elif champ.health >= num and not is_last_hitable(game, game.player, champ):
                return champ


def Ignite(game):
    ignite = game.player.get_summoner_spell(SummonerSpellType.Ignite)
    if ignite == None:
        return
    target = targeting.get_target(game, 550)
    if target and IsReady(game, ignite):
        IGdamage = 50 + 20 * GetLocalPlayerLevel() - (target.health_regen * 3)
        if target.health <= IGdamage:
            ignite.move_and_trigger(game.world_to_screen(target.pos))


def lview_update(game, ui):
    global auto_heal, heal_percent, show_healable, auto_barrier

    self = game.player

    if self.is_alive and self.is_visible and game.is_point_on_screen(self.pos):
        Ignite(game)
        if auto_heal:
            AutoHeal(game)
        if auto_barrier:
            AutoBarrier(game)
