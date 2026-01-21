# battlefield.py
import time, random
from entity import Entity
from priest import Priest
from mechanist import Mechanist
from intern import Intern
from gods import get_all_gods
from gods import Brahma, Vishnu, Shiva
from cosmic_event import CosmicEvent

def print_status(entities, turn):
    print("\n" + "="*70)
    print(f"Turn {turn} Summary:")
    print("="*70)
    print(f"{'Name':<15} | {'Health':>8} | {'Mana':>8} | {'Karma':>6} | {'Stamina':>8}")
    print("-"*70)
    for e in entities:
        print(f"{e.name:<15} | {e.health:8.1f} | {e.mana:8.1f} | {e.karma:6} | {e.stamina:8.1f}")
    print("="*70 + "\n")

def print_deity_stats(brahma, vishnu, shiva):
    print("\n" + "="*70)
    print("Divine Intervention Summary:")
    print("="*70)
    print(f"Brahma: Interventions = {brahma.interventions}, Total Health Restored = {brahma.total_health_restored:.1f}, Remaining Energy = {brahma.divine_energy:.1f}")
    print(f"Vishnu: Interventions = {vishnu.interventions}, Total Mana Granted = {vishnu.total_mana_granted:.1f}, Total Health Healed = {vishnu.total_health_healed:.1f}, Remaining Energy = {vishnu.divine_energy:.1f}")
    print(f"Shiva: Interventions = {shiva.interventions}, Total Decay Inflicted = {shiva.total_decay_inflicted:.1f}, Remaining Energy = {shiva.divine_energy:.1f}")
    print("="*70 + "\n")

def main():
    config1 = {
        "max_health": 120, "attack": 25, "defense": 8, "healing_ability": 20,
        "max_mana": 100, "mana_cost": 25, "special_attack_damage": 45,
        "karma": 50, "max_stamina": 100, "accuracy": 0.8, "evasion": 0.1, "critical_chance": 0.15
    }
    config2 = {
        "max_health": 110, "attack": 23, "defense": 10, "healing_ability": 18,
        "max_mana": 110, "mana_cost": 30, "special_attack_damage": 40,
        "karma": 50, "max_stamina": 100, "accuracy": 0.82, "evasion": 0.12, "critical_chance": 0.12
    }
    gods = get_all_gods()
    entity1 = Priest("High Priest Tenzin", gods=gods, config=config1)
    entity2 = Entity("Entity2", config=config2)
    entity3 = Mechanist("Entity3")
    entity4 = Intern("Intern Greg")

    entities = [entity1, entity2, entity3, entity4]

    brahma = gods["brahma"]
    vishnu = gods["vishnu"]
    shiva = gods["shiva"]
    cosmic = CosmicEvent()
    turn = 0
    max_turns = 50

    while len([e for e in entities if e.is_alive()]) > 1 and turn < max_turns:
        turn += 1
        print(f"\n{'-'*20} Turn {turn} {'-'*20}\n")
        cosmic.apply_event(entity1, entity2, brahma, vishnu, shiva)

        for e in entities:
            if not e.is_alive():
                continue
            opponents = [op for op in entities if op != e and op.is_alive()]
            if opponents:
                target = random.choice(opponents)
                if isinstance(e, Priest) and turn % 4 == 0:
                    e.ability(target)
                else:
                    e.take_turn(target)

        favored = random.choices([entity1, entity2], weights=[0.6, 0.4])[0]
        others = [e for e in entities if e != favored and e.is_alive()]
        if others:
            target = random.choice(others)
            brahma.influence_battle(favored, target)
            vishnu.influence_battle(favored, target)
            shiva.influence_battle(favored, target)

        if turn % 5 == 0:
            if entity1.health < 50 and entity1.inventory.get("health_potion", 0) < 1 and entity2.inventory.get("health_potion", 0) > 0:
                offer = {"mana_potion": 1}
                request = {"health_potion": 1}
                if entity1.propose_trade(entity2, offer, request):
                    entity2.accept_trade(entity1, offer, request)

        print_status(entities, turn)
        time.sleep(1)

    alive = [e for e in entities if e.is_alive()]
    if len(alive) == 1:
        print(f"{alive[0].name} wins after {turn} turns!")
    else:
        print("After 50 intense turns, the war ends in a stalemate!")

    print_deity_stats(brahma, vishnu, shiva)

if __name__ == "__main__":
    main()
