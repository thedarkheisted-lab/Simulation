# shiva.py
import random
from gods.brahma import get_priority_score

class Shiva:
    def __init__(self):
        self.name = "Shiva"
        self.cooldown = 0
        self.divine_energy = 90.0
        self.interventions = 0
        self.total_decay_inflicted = 0.0
        self.cost_multiplier = 1.0

    def influence_battle(self, c1, c2):
        if self.cooldown > 0 or self.divine_energy <= 0:
            self.cooldown = max(self.cooldown - 1, 0)
            return

        # Shiva punishes the lowest karma
        target = c1 if c1.karma < c2.karma else c2

        decay = 10 + (50 - target.karma) * 0.2 + random.uniform(-2, 2)
        decay = max(5, decay)
        target.take_damage(decay)
        self.total_decay_inflicted += decay

        cost = decay * 0.05 * self.cost_multiplier
        self.divine_energy -= cost
        self.interventions += 1

        print(f"{self.name} inflicts decay on {target.name}: -{decay:.1f} HP (Cost: {cost:.1f} energy)")
        self.cooldown = random.randint(1, 3)
