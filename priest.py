from entity import Entity

class Priest(Entity):
    def __init__(self, name, gods, logger=None):
            super().__init__(name, logger=logger)
            self.gods = gods or {}
            self.cooldown = 0

    def ability(self, target):
        if self.cooldown > 0:
            self.log(f"{self.name} is spiritually recharging. ({self.cooldown} turns left)")
            self.cooldown -= 1
            return

        if self.mana < 20:
            self.log(f"{self.name} whispers to the heavens... but lacks mana.")
            return

        self.mana -= 20
        success = False

        # Try Brahma first
        brahma = self.gods.get("brahma")
        if brahma and hasattr(brahma, "heal_entity"):
            healed = brahma.heal_entity(target)
            self.karma += 10
            self.log(f"{self.name} calls upon Brahma to heal {target.name} for {healed:.1f} HP.")
            success = True

        # If Vishnu is available and target is weak, try divine mana+health
        vishnu = self.gods.get("vishnu")
        if not success and vishnu and hasattr(vishnu, "bless_entity"):
            v_heal, v_mana = vishnu.bless_entity(target)
            self.karma += 8
            self.log(f"{self.name} invokes Vishnu to bless {target.name}: +{v_heal:.1f} HP, +{v_mana:.1f} Mana.")
            success = True

        # If Shiva is available and target's karma is cursed, trigger decay cleanse
        shiva = self.gods.get("shiva")
        if not success and shiva and hasattr(shiva, "cleanse_decay") and target.karma < 40:
            purified = shiva.cleanse_decay(target)
            self.karma += 5
            self.log(f"{self.name} begs Shiva to cleanse decay from {target.name}: +{purified:.1f} HP recovered.")
            success = True

        if success:
            self.cooldown = 3
        else:
            self.log(f"{self.name} prays desperately... but no god responds.")