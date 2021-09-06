from lview import *
from commons.targeting import TargetingConfig
from commons.items import *
from commons.skills import *
import json, time, math
from pprint import pprint
import win32api, win32con
from commons.damage_calculator import DamageSpecification
from commons.damage_calculator import DamageType

lview_script_info = {
    "script": "Caitlyn La Vegana",
    "author": "El Gordo Yogur",
    "description": "Se los Kitea a todos con una Verdura vegana Atomica",
    "target_champ": "caitlyn",
}

targeting = TargetingConfig()

cast_keys = {"W": 0, "E": 0, "Q": 0}
damageCalc = DamageSpecification()
damageType = DamageType.Normal


def is_ulteable(game, player, enemy):
    missile_speed = player.basic_missile_speed + 1.0
    atk_speed = player.base_atk_speed * player.atk_speed_multi

    damageCalc.damage_type = damageType
    damageCalc.base_damage = (player.base_atk + player.bonus_atk) - 0.33

    # TODO: integrate item onhit calculation based on damagetype
    hit_dmg = damageCalc.calculate_damage(player, enemy)
    hp = enemy.health
    t_until_basic_hits = game.distance(player, enemy) / missile_speed

    # where should we be applying client-server latency to the formula - in orbwalker or here?
    for missile in game.missiles:
        if missile.dest_id == enemy.id:
            src = game.get_obj_by_id(missile.src_id)
            if src:
                t_until_missile_hits = game.distance(missile, enemy) / (
                    (src.basic_missile_speed + 1.0) - 0.4
                )  # - 1.1 #Using src's basic missile speed is most reliable because different minion types have different missile speeds

                if t_until_missile_hits < t_until_basic_hits:
                    hp -= src.base_atk

    return hp - hit_dmg <= 0


def isulteableR(game):
    self = game.player
    target = None
    attrange = 3500
    for champ in game.champs:
        if (
            not champ.is_alive
            or not champ.is_visible
            or not champ.isTargetable
            or champ.is_ally_to(game.player)
            or game.player.pos.distance(champ.pos) > attrange
            or not is_ulteable(game, self, champ)
        ):
            continue
        if is_ulteable(game, self, champ):
            target = champ
    return target


VK_Q = 0x51  # Q Key
VK_W = 0x57  # W Key
VK_E = 0x45  # E Key
VK_R = 0x52  # R Key

VK_1 = 0x31  # 1 key
VK_2 = 0x32  # 2 key
VK_3 = 0x33  # 3 key
VK_4 = 0x34  # 4 key


def lview_load_cfg(cfg):
    global targeting, combo_key, only_r
    targeting.load_from_cfg(cfg)
    combo_key = cfg.get_int("combo_key", 0)
    only_r = cfg.get_int("only_r", 0)


def lview_save_cfg(cfg):
    global targeting, combo_key, only_r
    targeting.save_to_cfg(cfg)
    cfg.set_int("combo_key", combo_key)
    cfg.set_int("only_r", only_r)


def lview_draw_settings(game, ui):
    global targeting, combo_key, only_r
    targeting.draw(ui)
    combo_key = ui.keyselect("Combo key", combo_key)
    only_r = ui.keyselect("Only R key", only_r)


def lview_update(game, ui):
    if game.was_key_pressed(only_r):
        old_cpos = game.get_cursor()
        skill = getattr(game.player, "R")
        b_is_skillshot = is_skillshot(skill.name)
        skill_range = (
            get_skillshot_range(game, skill.name) if b_is_skillshot else 1500.0
        )
        target = isulteableR(game)
        if target:
            if skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0:
                cast_point = castpoint_for_collision(game, skill, game.player, target)
                if cast_point:
                    if b_is_skillshot:
                        cast_point = castpoint_for_collision(
                            game, skill, game.player, target
                        )
                    else:
                        cast_point = target.pos
                    cast_point = game.world_to_screen(cast_point)
                    game.move_cursor(cast_point)
                    win32api.keybd_event(VK_R, win32api.MapVirtualKey(VK_R, 0), 0, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(
                        VK_R,
                        win32api.MapVirtualKey(VK_R, 0),
                        win32con.KEYEVENTF_KEYUP,
                        0,
                    )
        time.sleep(0.01)
        game.move_cursor(old_cpos)
    if game.was_key_pressed(combo_key):
        old_cpos = game.get_cursor()
        for slot, key in cast_keys.items():
            skill = getattr(game.player, slot)
            b_is_skillshot = is_skillshot(skill.name)
            skill_range = (
                get_skillshot_range(game, skill.name) if b_is_skillshot else 1500.0
            )
            if slot == "Q":
                skill_range = 1250.0
            if slot == "W":
                skill_range = 800.0
            if slot == "E":
                skill_range = 750.0
            target = targeting.get_target(game, skill_range)
            if target:
                if int(skill.get_current_cooldown(game.time)) == 0 and skill.level > 0:
                    cast_point = castpoint_for_collision(
                        game, skill, game.player, target
                    )
                    if cast_point:
                        if b_is_skillshot:
                            cast_point = castpoint_for_collision(
                                game, skill, game.player, target
                            )
                        else:
                            cast_point = target.pos
                        cast_point = game.world_to_screen(cast_point)
                        game.draw_line(
                            cast_point,
                            game.world_to_screen(game.player.pos),
                            1.0,
                            Color.WHITE,
                        )
                        game.move_cursor(cast_point)
                        if slot == "W":
                            win32api.keybd_event(
                                VK_W, win32api.MapVirtualKey(VK_W, 0), 0, 0
                            )
                            time.sleep(0.05)
                            win32api.keybd_event(
                                VK_W,
                                win32api.MapVirtualKey(VK_W, 0),
                                win32con.KEYEVENTF_KEYUP,
                                0,
                            )

                        if slot == "E":
                            win32api.keybd_event(
                                VK_E, win32api.MapVirtualKey(VK_E, 0), 0, 0
                            )
                            time.sleep(0.05)
                            win32api.keybd_event(
                                VK_E,
                                win32api.MapVirtualKey(VK_E, 0),
                                win32con.KEYEVENTF_KEYUP,
                                0,
                            )

                        if slot == "Q":
                            win32api.keybd_event(
                                VK_Q, win32api.MapVirtualKey(VK_Q, 0), 0, 0
                            )
                            time.sleep(0.05)
                            win32api.keybd_event(
                                VK_Q,
                                win32api.MapVirtualKey(VK_Q, 0),
                                win32con.KEYEVENTF_KEYUP,
                                0,
                            )
                        time.sleep(0.01)
                        game.move_cursor(old_cpos)
