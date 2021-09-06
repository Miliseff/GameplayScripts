from lview import *
from commons.targeting import TargetingConfig
from commons.items import *
from commons.skills import *
import json, time, math
from pprint import pprint
import win32api, win32con

lview_script_info = {
    "script": "Brand",
    "author": "el gordo yogur veggie",
    "description": "se garcha a todos con brand",
    "target_champ": "brand",
}

targeting = TargetingConfig()

Q = {"Slot": "Q", "Range": 1100}
W = {"Slot": "W", "Range": 900}
E = {"Slot": "E", "Range": 675}
R = {"Slot": "R", "Range": 750}

def IsCollisioned(game, target, castpoint):
    self = game.player
    for minion in game.minions:
        if castpoint == None:
            continue
        if minion.is_enemy_to(game.player) and minion.is_alive:
            if point_on_line_segment(
                game.world_to_screen(self.pos),
                castpoint,
                game.world_to_screen(minion.pos),
                target.gameplay_radius * 1,
            ):
                return True
    return False
cast_keys = {"E": 0, "Q": 0, "W": 0, "R": 0}
VK_Q = 0x51  # Q Key
VK_W = 0x57  # W Key
VK_E = 0x45  # E Key
VK_R = 0x52  # R Key
VK_1 = 0x31  # 1 key
VK_2 = 0x32  # 2 key
VK_3 = 0x33  # 3 key
VK_4 = 0x34  # 4 key


clones = {
    "shaco": [0, False, False, "shaco_square"],
    "leblanc": [0, False, False, "leblanc_square"],
    "monkeyking": [0, False, False, "monkeyking_square"],
    "neeko": [0, False, False, "neeko_square"],
    "fiddlesticks": [0, False, False, "fiddlesticks_square"],
}

def GetBestTargetsInRange(game, atk_range=0):
    num = 999999999
    target = None
    if atk_range == 0:
        atk_range = game.player.atkRange + game.player.gameplay_radius
    for champ in game.champs:
        if champ.name in clones and champ.R.name == champ.D.name:
            continue
        if (
            not champ.is_alive
            or not champ.is_visible
            or not champ.isTargetable
            or champ.is_ally_to(game.player)
            or game.player.pos.distance(champ.pos) >= atk_range
        ):
            continue
        # if num < champ.health:
        #     num = champ.health
        #     target = champ
        if num >= champ.health:
            num = champ.health
            target = champ
        if IsImmobileTarget(champ):
            target = champ
        if is_last_hitable(game, game.player, champ):
            target = champ
    if target:
        return target

def RDamage(game, target):
    damage = 0
    if game.player.R.level == 1:
        damage = 100 + (
            get_onhit_physical(game.player, target)
            + get_onhit_magical(game.player, target)
        )
    elif game.player.R.level == 2:
        damage = 200 + (
            get_onhit_physical(game.player, target)
            + get_onhit_magical(game.player, target)
        )
    elif game.player.R.level == 3:
        damage = 300 + (
            get_onhit_physical(game.player, target)
            + get_onhit_magical(game.player, target)
        )
    return damage

def lview_load_cfg(cfg):
    global targeting, combo_key
    targeting.load_from_cfg(cfg)
    combo_key = cfg.get_int("combo_key", 0)


def lview_save_cfg(cfg):
    global targeting, combo_key
    targeting.save_to_cfg(cfg)
    cfg.set_int("combo_key", combo_key)


def lview_draw_settings(game, ui):
    global targeting, combo_key
    targeting.draw(ui)
    combo_key = ui.keyselect("Combo key", combo_key)


def lview_update(game, ui):
    if game.was_key_pressed(combo_key):
        q_spell = getSkill(game, "Q")
        w_spell = getSkill(game, "W")
        e_spell = getSkill(game, "E")
        r_spell = getSkill(game, "R")
        for slot, key in cast_keys.items():
            skill = getattr(game.player, slot)
            b_is_skillshot = is_skillshot(skill.name)
            skill_range = (
                get_skillshot_range(game, skill.name) if b_is_skillshot else 1500.0
            )
            if int(skill.get_current_cooldown(game.time)) == 0 and skill.level > 0:

                if slot == "E" and IsReady(game, e_spell):
                    target = GetBestTargetsInRange(game, E["Range"])
                    if target:
                       w_spell.move_and_trigger(game.world_to_screen(target.pos))
               
                if slot == "Q" and IsReady(game, q_spell):
                    target = GetBestTargetsInRange(game, Q["Range"])
                    if target:
                        if b_is_skillshot:
                            cast_point = getLinePrediction(game, skill, game.player, target)
                        if cast_point:
                            old_cpos = game.get_cursor()
                            if not IsCollisioned(game, target, cast_point):          
                                game.move_cursor(cast_point)
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
                                game.move_cursor(old_cpos)
                if slot == "W" and IsReady(game, w_spell):
                    target = GetBestTargetsInRange(game, W["Range"])
                    if target:
                        if b_is_skillshot:
                            cast_point = getLinePrediction(game, skill, game.player, target)
                        if cast_point:
                            old_cpos = game.get_cursor()
                            game.move_cursor(cast_point)
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
                            game.move_cursor(old_cpos)

                if slot == "R" and IsReady(game, r_spell): 
                    target = GetBestTargetsInRange(game, R["Range"])
                    if target and RDamage(game, target) >= target.health:
                        if b_is_skillshot:
                            cast_point = getLinePrediction(game, skill, game.player, target)
                        else:
                            cast_point = game.world_to_screen(target.pos)
                        if cast_point:
                            old_cpos = game.get_cursor()
                            game.move_cursor(cast_point)
                            win32api.keybd_event(
                                VK_R, win32api.MapVirtualKey(VK_R, 0), 0, 0
                            )
                            time.sleep(0.05)
                            win32api.keybd_event(
                                VK_R,
                                win32api.MapVirtualKey(VK_R, 0),
                                win32con.KEYEVENTF_KEYUP,
                                0,
                            )
                            game.move_cursor(old_cpos)
                time.sleep(0.05)
