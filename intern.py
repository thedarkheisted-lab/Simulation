# intern.py
from entity import Entity
import random

class Intern(Entity):
    def __init__(self, name="Unnamed Intern", config=None, logger=None):
        super().__init__(name, config=config or {}, logger=logger)
        self.title = "Intern"
        self.power_trip = False  # Tracks whether panic mode is active
        self.caffeine_level = 100  # Intern resource system (why not?)

    def take_turn(self, opponent):
        # 10% chance they forget to act at all
        if random.random() < 0.1:
            self.logger(f"{self.name}: Forgot what they were doing. Takes no action.")
            self.recover_stamina(5)
            return

        # If caffeine is low, activate PANIC PRODUCTIVITY MODE
        if self.caffeine_level < 30 and not self.power_trip:
            self.logger(f"{self.name} enters Panic Productivity mode!")
            self.power_trip = True
            self.attack *= 1.5
            self.accuracy += 0.1
            self.stamina += 20

        # Random chance to do something helpful... or not
        chance = random.random()
        if chance < 0.2:
            self.heal()
        elif chance < 0.4:
            self.rest()
        else:
            action = self.choose_attack(opponent)
            if action in self.attack_map:
                attack = self.attack_map[action]
                self.logger(f"{self.name}: Nervously attempting {action}...")
                attack.apply(self, opponent)

        self.caffeine_level = max(0, self.caffeine_level - random.uniform(5, 15))

    def reset_modifiers(self):
        super().reset_modifiers()
        if self.power_trip:
            self.logger(f"{self.name} crashes from caffeine overload. Back to normal.")
            self.power_trip = False
            self.caffeine_level = 100