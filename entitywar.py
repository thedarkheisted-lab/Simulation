import random
import time

class Entity:
    def __init__(self, name, health, attack, defense, healing_ability, mana, mana_cost, special_attack_damage):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.healing_ability = healing_ability
        self.mana = mana
        self.mana_cost = mana_cost
        self.special_attack_damage = special_attack_damage

    def take_damage(self, damage):
        self.health -= max(damage - self.defense, 0)

    def heal(self):
        self.health += self.healing_ability

    def attack_opponent(self, opponent):
        damage = self.attack
        opponent.take_damage(damage)
        print(f"{self.name} attacks {opponent.name} for {damage} damage!")

    def special_attack(self, opponent):
        if self.mana >= self.mana_cost and self.health >= 10:  # Check if enough mana and health
            self.mana -= self.mana_cost
            self.health -= 10  # Cost health to use the special attack
            opponent.take_damage(self.special_attack_damage)
            print(f"{self.name} uses special attack on {opponent.name} for {self.special_attack_damage} damage!")
        else:
            print(f"{self.name} tries to use special attack, but doesn't have enough mana or health.")

    def is_alive(self):
        return self.health > 0

    def take_turn(self, opponent):
        if self.health < 30:  # If health is low, heal
            self.heal()
            print(f"{self.name} heals!")
        elif self.mana >= self.mana_cost and self.health >= 10:  # If enough mana and health, use special attack
            self.special_attack(opponent)
        elif opponent.health < 30:  # If opponent is weak, attack
            self.attack_opponent(opponent)
        else:  # Otherwise, attack
            self.attack_opponent(opponent)

# Create two entities
entity1 = Entity("Entity1", 100, 20, 5, 15, 100, 30, 50)
entity2 = Entity("Entity2", 100, 15, 10, 10, 100, 30, 60)

# Simulate the battle
turn = 0
while entity1.is_alive() and entity2.is_alive():
    turn += 1
    print(f"\nTurn {turn}")
    if turn % 2 == 1:
        entity1.take_turn(entity2)
    else:
        entity2.take_turn(entity1)

    print(f"{entity1.name} Health: {entity1.health} Mana: {entity1.mana}")
    print(f"{entity2.name} Health: {entity2.health} Mana: {entity2.mana}")

    # Wait for a short period to make execution readable
    time.sleep(1)

# Declare winner
if entity1.is_alive():
    print(f"{entity1.name} wins!")
else:
    print(f"{entity2.name} wins!")
