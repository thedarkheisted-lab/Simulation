import random
import math

def variable_damage(base_damage, variance=0.1):
    variation = random.gauss(0, base_damage * variance)
    return max(0, base_damage + variation)

def fatigue_multiplier(entity):
    ratio = entity.stamina / entity.max_stamina
    return 0.5 + 0.5 * ratio


class BaseAttack:
    def __init__(self, name, stamina_cost=0, mana_cost=0, karma_cost=0):
        self.name = name
        self.stamina_cost = stamina_cost
        self.mana_cost = mana_cost
        self.karma_cost = karma_cost

    def check_resources(self, attacker):
        if attacker.stamina < self.stamina_cost:
            attacker.log(f"{attacker.name} lacks stamina for {self.name}!")
            return False
        if attacker.mana < self.mana_cost:
            attacker.log(f"{attacker.name} lacks mana for {self.name}!")
            return False
        return True

    def apply(self, attacker, defender):
        raise NotImplementedError("Subclasses must implement apply().")


class NormalAttack(BaseAttack):
    def __init__(self):
        super().__init__("Normal Attack", stamina_cost=10, karma_cost=5)

    def apply(self, attacker, defender):
        if not self.check_resources(attacker):
            return False
        attacker.stamina -= self.stamina_cost
        hit_chance = attacker.accuracy - defender.evasion
        if random.random() > hit_chance:
            attacker.karma -= 2
            attacker.log(f"{attacker.name}'s normal attack missed {defender.name}!")
            return False
        damage = variable_damage(attacker.attack, variance=0.2)
        actual = defender.take_damage(damage)
        attacker.karma -= self.karma_cost
        attacker.log(f"{attacker.name} used {self.name} for {actual:.1f} actual damage.")
        return True


class HeavyAttack(BaseAttack):
    def __init__(self):
        super().__init__("Heavy Attack", stamina_cost=20, karma_cost=7)

    def apply(self, attacker, defender):
        if not self.check_resources(attacker):
            return False
        attacker.stamina -= self.stamina_cost
        effective_accuracy = (attacker.accuracy * fatigue_multiplier(attacker)) - defender.evasion
        if random.random() > effective_accuracy:
            attacker.karma -= 3
            attacker.log(f"{attacker.name}'s heavy attack missed {defender.name}!")
            return False
        damage = variable_damage(attacker.attack * 1.5, variance=0.25) * fatigue_multiplier(attacker)
        actual = defender.take_damage(damage)
        attacker.karma -= self.karma_cost
        attacker.log(f"{attacker.name} used {self.name} for {actual:.1f} actual damage.")
        return True


class QuickAttack(BaseAttack):
    def __init__(self):
        super().__init__("Quick Attack", stamina_cost=5, karma_cost=3)

    def apply(self, attacker, defender):
        if not self.check_resources(attacker):
            return False
        attacker.stamina -= self.stamina_cost
        hit_chance = (attacker.accuracy - defender.evasion) * 1.1
        if random.random() > hit_chance:
            attacker.karma -= 1
            attacker.log(f"{attacker.name}'s quick attack missed {defender.name}!")
            return False
        damage = attacker.attack * 0.75
        actual = defender.take_damage(damage)
        attacker.karma -= self.karma_cost
        attacker.log(f"{attacker.name} used {self.name} for {actual:.1f} actual damage.")
        return True


class MagicAttack(BaseAttack):
    def __init__(self):
        super().__init__("Magic Attack", mana_cost=25, karma_cost=5)

    def apply(self, attacker, defender):
        if not self.check_resources(attacker):
            return False
        attacker.mana -= self.mana_cost
        hit_chance = attacker.accuracy - defender.evasion
        if random.random() > hit_chance:
            attacker.karma -= 4
            attacker.log(f"{attacker.name}'s magic attack missed {defender.name}!")
            return False
        damage = attacker.special_attack_damage
        actual = defender.take_damage(damage)
        attacker.karma -= self.karma_cost
        attacker.log(f"{attacker.name} used {self.name} for {actual:.1f} actual damage.")
        return True
