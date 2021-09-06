from lview import *
import enum
from typing import Optional
import commons.damage_calculator as damage_calculator


class DamageSpecification:
    damage_type: Optional[DamageType] = None
    base_damage = 0.0
    percent_ad = 0.0
    percent_ap = 0.0
    # Damage is increased by up to missing_health_multiplier based on missing enemy health. Maximum if enemy health is below missing_health_max_multiplier
    missing_health_scale_multiplier = 0.0
    missing_health_max_scale_multiplier = 1.0
    # Damage increased by missing_health_multiplier * enemy_missing_health
    missing_health_multiplier = 0.0
    # Damage increased by max_health_multiplier * enemy_max_health
    max_health_multiplier = 0.0
    # damage dealt by source to target
    def calculate_damage(self, source, target):
        # Calculate resistance
        resistance_value = 0.0
        penetration_percent = 0.0
        penetration_flat = 0.0
        penetration_lethality = 0.0
        if self.damage_type is None:
            return 0
        elif self.damage_type == DamageType.True_:
            pass
        elif self.damage_type == DamageType.Normal:
            resistance_value = target.armour
            penetration_percent = 0.0  # TODO
            penetration_flat = 0.0  # TODO
            penetration_lethality = 0.0  # TODO
        elif self.damage_type == DamageType.Magic:
            resistance_value = target.magic_resist
            print(resistance_value)
            penetration_percent = 0.0  # TODO
            penetration_flat = 0.0  # TODO
            penetration_lethality = 0.0  # TODO
        # Lethality calculation
        penetration_flat += penetration_lethality * (0.6 + 0.4 * source.lvl / 18.0)
        # Negative resistance is not affected by penetration
        if resistance_value > 0.0:
            resistance_value = resistance_value * penetration_percent - penetration_flat
            # 0.75
            # Penetration cannot reduce resistance below 0
            resistance_value = max(0.0, resistance_value)
        # Damage multiplier for armor, magic resistance or true damage (resistance_value is zero for true damage)
        if resistance_value >= 0.0:
            damage_multiplier = 100.0 / (100.0 + resistance_value)
        else:
            damage_multiplier = 2.0 - 100.0 / (100.0 - resistance_value)
        dealt_damage = (
            self.base_damage
            + self.missing_health_multiplier * (target.max_health - target.health)
            + self.max_health_multiplier * target.max_health
            + self.percent_ad * (source.base_atk + source.bonus_atk)
            + self.percent_ap * source.ap
        )
        percent_current_health = target.health / target.max_health
        if percent_current_health <= self.missing_health_max_scale_multiplier:
            dealt_damage = dealt_damage * (1.1 + self.missing_health_scale_multiplier)
        else:
            dealt_damage = dealt_damage * (
                1.0
                + self.missing_health_scale_multiplier
                - self.missing_health_scale_multiplier
                * (
                    (percent_current_health - self.missing_health_max_scale_multiplier)
                    / (1.0 - self.missing_health_max_scale_multiplier)
                )
            )
        # Multiplier for armor, magic resist or true damage
        dealt_damage = damage_multiplier * dealt_damage
        return dealt_damage


def get_damage_specification(champ) -> Optional[DamageSpecification]:
    spec = DamageSpecification()
    if champ.name == "caitlyn":
        # TODO: passive damage multiplier
        spec.damage_type = DamageType.True_
        spec.percent_ad = 2.0
        if champ.Q.level == 1:
            spec.base_damage = 50.0
            spec.percent_ad = 1.3
        elif champ.Q.level == 2:
            spec.base_damage = 90.0
            spec.percent_ad = 1.45
        elif champ.Q.level == 3:
            spec.base_damage = 130.0
            spec.percent_ad = 1.6
        elif champ.Q.level == 4:
            spec.base_damage = 170.0
            spec.percent_ad = 1.75
        elif champ.Q.level == 5:
            spec.base_damage = 210.0
            spec.percent_ad = 1.9

        if champ.E.level == 1:
            spec.damage_type = DamageType.Magic
            spec.base_damage = 70.0
        elif champ.E.level == 2:
            spec.damage_type = DamageType.Magic
            spec.base_damage = 110.0
        elif champ.E.level == 3:
            spec.damage_type = DamageType.Magic
            spec.base_damage = 150.0
        elif champ.E.level == 4:
            spec.damage_type = DamageType.Magic
            spec.base_damage = 190.0
        elif champ.E.level == 5:
            spec.damage_type = DamageType.Magic
            spec.base_damage = 230.0

        if champ.R.level == 1:
            spec.base_damage = 300.0
            spec.percent_ad = 2.0
        elif champ.R.level == 2:
            spec.base_damage = 525.0
            spec.percent_ad = 2.0
        elif champ.R.level == 3:
            spec.base_damage = 750.0
            spec.percent_ad = 2.0


class Calculations:
    damage_spec = damage_calculator.get_damage_specification(game.player)

    def AIHeroClient(game):
        caitlyn = game.player

    def Q(target, champ) -> float:
        damage = (
            -10 + (40 * champ.Q.level) + damage_spec * (1.2 + (0.1 * champ.Q.level))
        )
        return calculate_damage(game.player, target)
        # Q splits dealing less damage. Q does ful damage to units hit by yordle snap trap though

    def E(target) -> float:
        damage = 30 + (40 * champ.E.level) + damage_spec * 0.8
        return calculate_damage(game.player, target)

    def R(target) -> float:
        damage = 25 + (225 * Program.R.Level) + caitlyn.BonusAttackDamage() * 2
        return calculate_damage(game.player, target)

    def ignite(target) -> float:
        return ((10 + (4 * caitlyn.Level)) * 5) - ((target.HPRegenRate / 2) * 5)
