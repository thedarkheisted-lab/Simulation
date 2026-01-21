# cosmic_event.py
import random
import inspect

class BaseCosmicEvent:
    name = "Unnamed Event"
    description = "No description."
    duration = 1

    def apply(self, e1, e2, brahma, vishnu, shiva):
        pass

class CelestialAlignment(BaseCosmicEvent):
    name = "Celestial Alignment"
    description = "A rare alignment boosts combat effectiveness."

    def apply(self, e1, e2, *_):
        e1.attack *= 1.1
        e2.attack *= 1.1
        e1.mana = min(e1.mana + 5, e1.max_mana)
        e2.mana = min(e2.mana + 5, e2.max_mana)

class CosmicDrought(BaseCosmicEvent):
    name = "Cosmic Drought"
    description = "Cosmic energies are low; mana recovery suffers."

    def apply(self, e1, e2, *_):
        e1.attack *= 0.95
        e2.attack *= 0.95
        e1.mana = min(e1.mana - 5, e1.max_mana)
        e2.mana = min(e2.mana - 5, e2.max_mana)

class MysticWinds(BaseCosmicEvent):
    name = "Mystic Winds"
    description = "Evasive winds aid dodging—accuracy and evasion are slightly improved."

    def apply(self, e1, e2, *_):
        e1.accuracy += 0.05
        e2.accuracy += 0.05
        e1.evasion += 0.05
        e2.evasion += 0.05

class AstralSurge(BaseCosmicEvent):
    name = "Astral Surge"
    description = "A surge of astral energy empowers divine intervention, reducing their cost by 50% this turn."

    def apply(self, *_entities, brahma, vishnu, shiva):
        brahma.cost_multiplier = 0.5
        vishnu.cost_multiplier = 0.5
        shiva.cost_multiplier = 0.5

class TemporalFlux(BaseCosmicEvent):
    name = "Temporal Flux"
    description = "Time seems to slow, allowing better recovery of stamina."

    def apply(self, e1, e2, *_):
        e1.recover_stamina(10)
        e2.recover_stamina(10)

class CosmicEvent:
    def __init__(self):
        self.events = [
            CelestialAlignment(),
            CosmicDrought(),
            MysticWinds(),
            AstralSurge(),
            TemporalFlux()
        ]

    def apply_event(self, e1, e2, brahma, vishnu, shiva):
        e1.reset_modifiers()
        e2.reset_modifiers()

        event = random.choice(self.events)
        print(f"\n*** Cosmic Event: {event.name} - {event.description} ***")

    # Inspect the method signature
        apply_sig = inspect.signature(event.apply)
        if 'brahma' in apply_sig.parameters:
            event.apply(e1, e2, brahma=brahma, vishnu=vishnu, shiva=shiva)
        else:
            event.apply(e1, e2)

        return event