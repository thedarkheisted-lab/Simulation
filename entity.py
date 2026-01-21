import random
from attack_types import NormalAttack, HeavyAttack, QuickAttack, MagicAttack

def weighted_choice(choices):
    total = sum(weight for action, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for action, weight in choices:
        if upto + weight >= r:
            return action
        upto += weight
    return choices[-1][0]

class Entity:
    def __init__(self, name, config=None, logger = None):
        config = config or {}

        self.name = name
        self.player_id = config.get("player_id")
        self.faction = config.get("faction", "Neutral")
        self.logger = logger or config.get("logger", print)

        # Core stats
        self.max_health = config.get("max_health", 120)
        self.health = self.max_health
        self.base_attack = config.get("attack", 25)
        self.attack = self.base_attack
        self.defense = config.get("defense", 8)

        # Mana / stamina systems
        self.max_mana = config.get("max_mana", 100)
        self.mana = self.max_mana
        self.max_stamina = config.get("max_stamina", 100)
        self.stamina = self.max_stamina
        self.mana_cost = config.get("mana_cost", 25)

        # Special abilities
        self.special_attack_damage = config.get("special_attack_damage", 45)
        self.healing_ability = config.get("healing_ability", 20)
        self.karma = config.get("karma", 50)

        # Combat dynamics
        self.base_accuracy = config.get("accuracy", 0.8)
        self.accuracy = self.base_accuracy
        self.base_evasion = config.get("evasion", 0.1)
        self.evasion = self.base_evasion
        self.critical_chance = config.get("critical_chance", 0.15)
        self.heal_turns = 0

        # Inventory system
        self.inventory = {
            "health_potion": 2,
            "mana_potion": 2,
            "stamina_boost": 1,
            "karma_scroll": 1,
        }
        self.attack_map = {
            "normal_attack": NormalAttack(),
            "heavy_attack": HeavyAttack(),
            "quick_attack": QuickAttack(),
            "magic_attack": MagicAttack()
        }

    def __str__(self):
        return f"{self.name} | HP: {self.health:.1f}/{self.max_health} | Mana: {self.mana:.1f} | Stamina: {self.stamina:.1f} | Karma: {self.karma}"

    def log(self, message):
        self.logger(f"{self.name}: {message}")

    def recover_stamina(self, amount=10):
        self.stamina = min(self.stamina + amount, self.max_stamina)

    def reset_modifiers(self):
        self.attack = self.base_attack
        self.accuracy = self.base_accuracy
        self.evasion = self.base_evasion

    def rest(self):
        recovered_stamina = random.uniform(15, 25)
        recovered_mana = random.uniform(5, 10)
        self.stamina = min(self.stamina + recovered_stamina, self.max_stamina)
        self.mana = min(self.mana + recovered_mana, self.max_mana)
        self.log(f"{self.name} rests and recovers {recovered_stamina:.1f} stamina and {recovered_mana:.1f} mana.")

    def take_damage(self, damage):
        actual_damage = max(damage - self.defense, 0)
        blocked = max(0, damage - actual_damage)
        self.health = max(0, self.health - actual_damage)
        self.log(f"{self.name} takes {actual_damage:.1f} damage (blocked {blocked:.1f})")
        return actual_damage

    def heal(self):
        healed = min(self.healing_ability, self.max_health - self.health)
        self.health += healed
        self.heal_turns += 1
        self.karma += 5
        self.recover_stamina(15)
        self.log(f"{self.name} heals for {healed} (Health: {self.health:.1f}), karma now {self.karma}.")

    def defend(self):
        self.defense += 5
        self.stamina -= 5
        self.log(f"{self.name} takes a defensive stance, boosting defense temporarily.")

    def choose_attack(self, opponent):
        attack_options = []
        if self.stamina >= 20:
            attack_options.append(("heavy_attack", 0.3))
        if self.mana >= self.mana_cost:
            attack_options.append(("magic_attack", 0.3))
        if self.stamina >= 5:
            attack_options.append(("quick_attack", 0.3))
        if self.stamina >= 10:
            attack_options.append(("normal_attack", 0.4))
        if not attack_options:
            return "rest"
        return weighted_choice(attack_options)

    def choose_action(self, opponent):
        actions = []
        health_ratio = self.health / self.max_health
        if health_ratio < 0.4:
            actions.append(("heal", 0.6))
        if self.stamina < 10:
            actions.append(("rest", 0.8))
        if self.stamina >= 20:
            actions.append(("heavy_attack", 0.3))
        if self.mana >= self.mana_cost:
            actions.append(("magic_attack", 0.3))
        if self.stamina >= 5:
            actions.append(("quick_attack", 0.3))
        if self.stamina >= 10:
            actions.append(("normal_attack", 0.4))
        if not actions:
            actions.append(("defend", 0.5))
        return weighted_choice(actions)

    def take_turn(self, opponent):
        if self.health < 40 and self.inventory.get("health_potion", 0) > 0:
            self.use_health_potion()
        elif self.mana < 30 and self.inventory.get("mana_potion", 0) > 0:
            self.use_mana_potion()
        elif self.stamina < 20 and self.inventory.get("stamina_boost", 0) > 0:
            self.use_stamina_boost()
        else:
            action = self.choose_action(opponent)

            if action == "heal":
                self.heal()
            elif action == "rest":
                self.rest()
            elif action == "defend":
                self.defend()
            elif action in self.attack_map:
                attack = self.attack_map[action]
                attack.apply(self, opponent)

        self.recover_stamina(random.uniform(5, 10))

    def is_alive(self):
        return self.health > 0

    # === Trade ===
    def propose_trade(self, other, offer, request):
        if all(self.inventory.get(item, 0) >= qty for item, qty in offer.items()) and \
           all(other.inventory.get(item, 0) >= qty for item, qty in request.items()):
            self.log(f"{self.name} proposes trade to {other.name}: {offer} for {request}")
            return True
        self.log(f"{self.name}'s trade proposal failed due to insufficient items.")
        return False

    def accept_trade(self, other, offer, request):
        for item, qty in offer.items():
            self.inventory[item] = self.inventory.get(item, 0) + qty
            other.inventory[item] -= qty
        for item, qty in request.items():
            self.inventory[item] -= qty
            other.inventory[item] = other.inventory.get(item, 0) + qty
        self.log(f"{self.name} accepted trade with {other.name}: {offer} for {request}")

    # === Items ===
    def use_health_potion(self):
        if self.inventory.get("health_potion", 0) > 0:
            healed = min(30, self.max_health - self.health)
            self.health += healed
            self.inventory["health_potion"] -= 1
            self.log(f"{self.name} uses a health potion and heals {healed} HP.")
        else:
            self.log(f"{self.name} has no health potions!")

    def use_mana_potion(self):
        if self.inventory.get("mana_potion", 0) > 0:
            recovered = min(25, self.max_mana - self.mana)
            self.mana += recovered
            self.inventory["mana_potion"] -= 1
            self.log(f"{self.name} uses a mana potion and recovers {recovered} mana.")
        else:
            self.log(f"{self.name} has no mana potions!")

    def use_stamina_boost(self):
        if self.inventory.get("stamina_boost", 0) > 0:
            recovered = min(20, self.max_stamina - self.stamina)
            self.stamina += recovered
            self.inventory["stamina_boost"] -= 1
            self.log(f"{self.name} uses a stamina boost and recovers {recovered} stamina.")
        else:
            self.log(f"{self.name} has no stamina boosts!")
