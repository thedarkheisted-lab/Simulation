from entity import Entity
import random

class Mechanist(Entity):
    def __init__(self, name="The Mechanist", config=None, logger = None):
        config = config or {}
        config.update({
            "max_health": 110,
            "attack": 28,
            "defense": 10,
            "max_mana": 0,  # No divine connection
            "mana": 0,
            "karma": 0,
            "max_stamina": 120,
            "healing_ability": 0,
            "accuracy": 0.95,
            "evasion": 0.1,
            "critical_chance": 0.0  # No drama, just math
        })
        super().__init__(name, config={"logger": logger})
        self.overclocked = True
        self.charge = 0

        self.heat = 0  # Used instead of mana
        self.cooldowns = {
            "emp": 0,
            "overdrive": 0
        }

    def take_turn(self, opponent):
        self.heat += 5

        if self.health < 40 and self.cooldowns["overdrive"] == 0:
            self.overdrive(opponent)
            self.cooldowns["overdrive"] = 4
        elif opponent.mana > 0 and self.cooldowns["emp"] == 0:
            self.emp_pulse(opponent)
            self.cooldowns["emp"] = 3
        else:
            action = self.choose_action(opponent)
            if action in self.attack_map:
                attack = self.attack_map[action]
                attack.apply(self, opponent)
            else:
                self.rest()

        # Cooldowns tick down
        for skill in self.cooldowns:
            if self.cooldowns[skill] > 0:
                self.cooldowns[skill] -= 1

        self.recover_stamina(random.uniform(7, 12))

    def emp_pulse(self, opponent):
        opponent.mana = max(0, opponent.mana - 20)
        self.logger(f"{self.name} emits an EMP pulse, disabling {opponent.name}'s magic channels!")

    def overdrive(self, opponent):
        damage = 40 + self.heat * 0.2
        self.heat = 0
        actual = opponent.take_damage(damage)
        self.logger(f"{self.name} activates Overdrive! Unleashes {actual:.1f} damage using excess heat.")

    def heal(self):
        # Converts healing attempts into stamina
        self.recover_stamina(20)
        self.logger(f"{self.name} reroutes divine healing into mechanical stamina recovery.")

    def use_health_potion(self):
        # Same as base but logs differently
        if self.inventory.get("health_potion", 0) > 0:
            healed = min(30, self.max_health - self.health)
            self.health += healed
            self.inventory["health_potion"] -= 1
            self.logger(f"{self.name} applies a nano-repair gel and restores {healed} HP.")
        else:
            self.logger(f"{self.name} has no repair gels available.")

    def reset_modifiers(self):
        super().reset_modifiers()
        # Optional: reset heat on new divine event? Maybe not. Leave it building.

    def is_cyborg(self):
        return True
