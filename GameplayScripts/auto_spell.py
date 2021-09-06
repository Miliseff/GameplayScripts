from lview import *
from commons.targeting import TargetingConfig
from commons.skills import *
import json, time
import win32api, win32con
from pprint import pprint

lview_script_info = {
    "script": "Auto Spell",
    "author": "leryss",
    "description": "Automatically casts spells on targets. Skillshots are cast using movement speed prediction. Works great for MOST skills but fails miserably for a few (for example yuumis Q)",
}

targeting = TargetingConfig()
cast_keys = {"Q": 0, "W": 0, "E": 0, "R": 0}

VK_Q = 0x51  # Q Key
VK_W = 0x57  # W Key
VK_E = 0x45  # E Key
VK_R = 0x52  # R Key


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

def lview_load_cfg(cfg):
    global targeting, cast_keys
    targeting.load_from_cfg(cfg)
    cast_keys = json.loads(cfg.get_str("cast_keys", json.dumps(cast_keys)))


def lview_save_cfg(cfg):
    global targeting, cast_keys
    targeting.save_to_cfg(cfg)
    cfg.set_str("cast_keys", json.dumps(cast_keys))


def lview_draw_settings(game, ui):
    global targeting, cast_keys
    targeting.draw(ui)
    for slot, key in cast_keys.items():
        cast_keys[slot] = ui.keyselect(f"Key to cast {slot}", key)
    draw_prediction_info(game, ui)


def combo(self, game):
    self.castSkill(game, "E")
    self.castSkill(game, "W")
    self.castSkill(game, "Q")


def skPrediction(self, game, skill, slot):
    skill = getattr(game.player, slot)
    b_is_skillshot = is_skillshot(skill.name)
    skill_range = get_skillshot_range(game, skill.name) if b_is_skillshot else 1500.0
    if slot == "Q":
        skill_range = 600.0
    target = self.targeting.get_target(game, skill_range)
    if target:
        if skill.get_current_cooldown(game.time) == 0.0 and skill.level > 0:
            cast_point = castpoint_for_collision(game, skill, game.player, target)
            if b_is_skillshot:
                cast_point = castpoint_for_collision(game, skill, game.player, target)
            else:
                cast_point = target.pos
            cast_point = game.world_to_screen(cast_point)
            return cast_point


def lview_update(game, ui):
    if game.isChatOpen:
        return
    global targeting, cast_keys

    for slot, key in cast_keys.items():
        if game.was_key_pressed(key):
            skill = getattr(game.player, slot)
            b_is_skillshot = is_skillshot(skill.name)
            #print(skill.name)
            skill_range = (
                get_skillshot_range(game, skill.name) if b_is_skillshot else 1500.0
            )
            target = targeting.get_target(game, skill_range)
            if target:
                if b_is_skillshot:
                    cast_point = getLinePrediction(
                        game, skill, game.player, target
                    )
                    if IsCollisioned(game, target, cast_point):
                        continue
                else:
                    cast_point = game.world_to_screen(target.pos)

                if cast_point:
                    old_cpos = game.get_cursor()
                    game.move_cursor(cast_point)
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
                    if slot == "R":
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

                    time.sleep(0.01)
                    game.move_cursor(old_cpos)
