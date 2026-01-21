# vishnu.py
import random
from gods.brahma import get_priority_score

class Vishnu:
    def __init__(self):
        self.name = "Vishnu"
        self.cooldown = 0
        self.divine_energy = 120.0
        self.interventions = 0
        self.total_mana_granted = 0.0
        self.total_health_healed = 0.0
        self.cost_multiplier = 1.0

    def influence_battle(self, c1, c2):
        if self.cooldown > 0 or self.divine_energy <= 0:
            self.cooldown = max(self.cooldown - 1, 0)
            return

        targets = sorted([(c1, get_priority_score(c1)), (c2, get_priority_score(c2))],
                         key=lambda x: x[1], reverse=True)
        target, score = targets[0]

        if target.health < 0.5 * target.max_health:
            heal_amt = 15 * (1 + (target.karma - 50) / 100.0 + random.uniform(-0.1, 0.1))
            before = target.health
            target.health = min(target.health + heal_amt, target.max_health)
            actual_heal = target.health - before
            self.total_health_healed += actual_heal
            cost = actual_heal * 0.1 * self.cost_multiplier
            self.divine_energy -= cost
            print(f"{self.name} heals {target.name} for {actual_heal:.1f} health. (Cost: {cost:.1f} energy)")
        else:
            mana_amt = 10 * (1 + (target.karma - 50) / 100.0 + random.uniform(-0.1, 0.1))
            before = target.mana
            target.mana = min(target.mana + mana_amt, target.max_mana)
            granted = target.mana - before
            self.total_mana_granted += granted
            cost = granted * 0.1 * self.cost_multiplier
            self.divine_energy -= cost
            print(f"{self.name} grants mana to {target.name}: +{granted:.1f} MP (Cost: {cost:.1f} energy)")

        self.interventions += 1
        self.cooldown = random.randint(1, 3)
