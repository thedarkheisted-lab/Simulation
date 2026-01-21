# brahma.py
import random

def get_priority_score(entity):
    health_ratio = entity.health / entity.max_health
    karma_weight = entity.karma / 100  # scale 0–1
    danger_score = 1 - health_ratio
    critical_bonus = 0.3 if entity.health < 0.2 * entity.max_health else 0
    return danger_score + (karma_weight * 0.5) + critical_bonus

class Brahma:
    def __init__(self):
        self.name = "Brahma"
        self.cooldown = 0
        self.divine_energy = 100.0
        self.interventions = 0
        self.total_health_restored = 0.0
        self.cost_multiplier = 1.0

    def influence_battle(self, c1, c2):
        if self.cooldown > 0 or self.divine_energy <= 0:
            self.cooldown = max(self.cooldown - 1, 0)
            return

        priorities = sorted([(c1, get_priority_score(c1)), (c2, get_priority_score(c2))],
                            key=lambda x: x[1], reverse=True)
        target, score = priorities[0]

        if score < 0.4:
            print(f"{self.name} finds no mortal worthy of aid.")
            return

        heal_amt = 20 + random.uniform(-5, 5)
        before = target.health
        target.health = min(target.health + heal_amt, target.max_health)
        actual_heal = target.health - before

        cost = actual_heal * 0.2 * self.cost_multiplier
        self.divine_energy -= cost
        self.total_health_restored += actual_heal
        self.interventions += 1

        print(f"{self.name} heals {target.name} for {actual_heal:.1f} HP. (Cost: {cost:.1f} energy)")
        self.cooldown = random.randint(1, 3)
