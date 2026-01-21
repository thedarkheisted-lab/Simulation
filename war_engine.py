import random
from dataclasses import dataclass
from typing import Callable, List

from cosmic_event import CosmicEvent
from entity import Entity
from gods import get_all_gods
from intern import Intern
from mechanist import Mechanist
from priest import Priest


@dataclass
class CosmicEventInfo:
    name: str
    description: str


class WarEngine:
    def __init__(
        self,
        logger: Callable[[str], None] = print,
        seed: int | None = None,
        max_turns: int = 50,
    ) -> None:
        if seed is not None:
            random.seed(seed)

        self._events: List[str] = []
        self._logger = logger
        self.max_turns = max_turns
        self.turn = 0
        self.current_event: CosmicEventInfo | None = None

        self.gods = get_all_gods(logger=self._log)
        self.cosmic = CosmicEvent(logger=self._log)

        self.entity1 = Priest("High Priest Tenzin", gods=self.gods, logger=self._log)
        self.entity2 = Entity("Entity2", logger=self._log)
        self.entity3 = Mechanist("Arthur 2.0", logger=self._log)
        self.entity4 = Intern("Intern Greg", logger=self._log)

        self.entities = [self.entity1, self.entity2, self.entity3, self.entity4]

    def _log(self, message: str) -> None:
        self._events.append(message)
        self._logger(message)

    def _format_status(self) -> str:
        header = [
            "\n" + "=" * 70,
            f"Turn {self.turn} Summary:",
            "=" * 70,
            f"{'Name':<15} | {'Health':>8} | {'Mana':>8} | {'Karma':>6} | {'Stamina':>8}",
            "-" * 70,
        ]
        rows = [
            f"{e.name:<15} | {e.health:8.1f} | {e.mana:8.1f} | {e.karma:6} | {e.stamina:8.1f}"
            for e in self.entities
        ]
        footer = "=" * 70 + "\n"
        return "\n".join(header + rows + [footer])

    def is_over(self) -> bool:
        alive = [e for e in self.entities if e.is_alive()]
        return len(alive) <= 1 or self.turn >= self.max_turns

    def step(self) -> List[str]:
        if self.is_over():
            return []

        self._events = []
        self.turn += 1
        self._log(f"\n{'-' * 20} Turn {self.turn} {'-' * 20}\n")

        event = self.cosmic.apply_event(
            self.entity1,
            self.entity2,
            self.gods["brahma"],
            self.gods["vishnu"],
            self.gods["shiva"],
        )
        if event:
            self.current_event = CosmicEventInfo(event.name, event.description)

        for entity in self.entities:
            if not entity.is_alive():
                continue
            opponents = [e for e in self.entities if e != entity and e.is_alive()]
            if opponents:
                target = random.choice(opponents)
                entity.take_turn(target)

        favored_target = self.entity1
        possible_targets = [e for e in self.entities if e != favored_target and e.is_alive()]
        for god in self.gods.values():
            if possible_targets:
                god_opponent = random.choice(possible_targets)
                god.influence_battle(favored_target, god_opponent)

        if self.turn % 5 == 0:
            if (
                self.entity1.health < 50
                and self.entity1.inventory.get("health_potion", 0) < 1
                and self.entity2.inventory.get("health_potion", 0) > 0
            ):
                offer = {"mana_potion": 1}
                request = {"health_potion": 1}
                if self.entity1.propose_trade(self.entity2, offer, request):
                    self.entity2.accept_trade(self.entity1, offer, request)

        self._log(self._format_status())

        if self.is_over():
            alive = [e for e in self.entities if e.is_alive()]
            if len(alive) == 1:
                self._log(f"{alive[0].name} wins after {self.turn} turns!")
            else:
                self._log("After 50 intense turns, the war ends in a stalemate!")

        return list(self._events)
