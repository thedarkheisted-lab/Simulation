import argparse
import random
import re
import sqlite3
import time
from pathlib import Path

from cosmic_event import CosmicEvent
from entity import Entity
from gods import get_all_gods
from intern import Intern
from mechanist import Mechanist
from priest import Priest


class GregNotesLogger:
    def __init__(self, db_path: Path, observer: str = "orchestrator"):
        self.db_path = Path(db_path)
        self.observer = observer
        self.current_turn = 0
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    turn INTEGER,
                    event_type TEXT,
                    source TEXT,
                    target TEXT,
                    value REAL,
                    context TEXT,
                    observer TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def set_turn(self, turn: int) -> None:
        self.current_turn = turn

    def log_event(
        self,
        event_type: str,
        source: str | None = None,
        target: str | None = None,
        value: float | None = None,
        context: str | None = None,
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO notes (turn, event_type, source, target, value, context, observer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.current_turn,
                    event_type,
                    source,
                    target,
                    value,
                    context,
                    self.observer,
                ),
            )

    def _parse_message(self, message: str) -> tuple[str, str | None, str | None, float | None]:
        trimmed = message.strip()
        source = None
        target = None
        value = None
        event_type = "log"

        if ": " in trimmed:
            source, trimmed = trimmed.split(": ", 1)

        if trimmed.startswith("*** Cosmic Event:"):
            event_type = "cosmic_event"
        elif source in {"Brahma", "Vishnu", "Shiva"}:
            event_type = "divine"
        elif "takes" in trimmed and "damage" in trimmed:
            event_type = "damage"

        if not source:
            maybe_source = trimmed.split(" ", 1)[0]
            if maybe_source in {"Brahma", "Vishnu", "Shiva"}:
                source = maybe_source

        heal_match = re.search(r"heals (?P<target>.+?) for (?P<value>[\d.]+)", trimmed)
        mana_match = re.search(r"grants mana to (?P<target>.+?): \+(?P<value>[\d.]+)", trimmed)
        decay_match = re.search(r"inflicts decay on (?P<target>.+?): -(?P<value>[\d.]+)", trimmed)
        damage_match = re.search(r"takes (?P<value>[\d.]+) damage", trimmed)

        match = heal_match or mana_match or decay_match or damage_match
        if match:
            if "target" in match.groupdict():
                target = match.group("target")
            value = float(match.group("value"))

        return event_type, source, target, value

    def __call__(self, message: str) -> None:
        event_type, source, target, value = self._parse_message(message)
        self.log_event(
            event_type=event_type,
            source=source,
            target=target,
            value=value,
            context=message.strip(),
        )
        print(message)


def _format_status(entities: list[Entity], turn: int) -> str:
    header = [
        "\n" + "=" * 70,
        f"Turn {turn} Summary:",
        "=" * 70,
        f"{'Name':<15} | {'Health':>8} | {'Mana':>8} | {'Karma':>6} | {'Stamina':>8}",
        "-" * 70,
    ]
    rows = [
        f"{e.name:<15} | {e.health:8.1f} | {e.mana:8.1f} | {e.karma:6} | {e.stamina:8.1f}"
        for e in entities
    ]
    footer = "=" * 70 + "\n"
    return "\n".join(header + rows + [footer])


def run_simulation(max_turns: int, delay: float, seed: int | None, db_path: Path) -> None:
    if seed is not None:
        random.seed(seed)

    logger = GregNotesLogger(db_path)
    gods = get_all_gods(logger=logger)

    config1 = {
        "max_health": 120,
        "attack": 25,
        "defense": 8,
        "healing_ability": 20,
        "max_mana": 100,
        "mana_cost": 25,
        "special_attack_damage": 45,
        "karma": 50,
        "max_stamina": 100,
        "accuracy": 0.8,
        "evasion": 0.1,
        "critical_chance": 0.15,
        "logger": logger,
    }
    config2 = {
        "max_health": 110,
        "attack": 23,
        "defense": 10,
        "healing_ability": 18,
        "max_mana": 110,
        "mana_cost": 30,
        "special_attack_damage": 40,
        "karma": 50,
        "max_stamina": 100,
        "accuracy": 0.82,
        "evasion": 0.12,
        "critical_chance": 0.12,
        "logger": logger,
    }

    entity1 = Priest("High Priest Tenzin", gods=gods, config=config1, logger=logger)
    entity2 = Entity("Entity2", config=config2, logger=logger)
    entity3 = Mechanist("Entity3", logger=logger)
    entity4 = Intern("Intern Greg", logger=logger)

    entities = [entity1, entity2, entity3, entity4]
    brahma = gods["brahma"]
    vishnu = gods["vishnu"]
    shiva = gods["shiva"]
    cosmic = CosmicEvent(logger=logger)

    turn = 0
    while len([e for e in entities if e.is_alive()]) > 1 and turn < max_turns:
        turn += 1
        logger.set_turn(turn)
        logger.log_event(event_type="turn_start", context=f"Turn {turn} start.")
        print(f"\n{'-' * 20} Turn {turn} {'-' * 20}\n")

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
            if (
                entity1.health < 50
                and entity1.inventory.get("health_potion", 0) < 1
                and entity2.inventory.get("health_potion", 0) > 0
            ):
                offer = {"mana_potion": 1}
                request = {"health_potion": 1}
                if entity1.propose_trade(entity2, offer, request):
                    entity2.accept_trade(entity1, offer, request)

        summary = _format_status(entities, turn)
        print(summary)
        logger.log_event(event_type="turn_summary", context=summary)

        if delay > 0:
            time.sleep(delay)

    alive = [e for e in entities if e.is_alive()]
    if len(alive) == 1:
        final_message = f"{alive[0].name} wins after {turn} turns!"
    else:
        final_message = "After 50 intense turns, the war ends in a stalemate!"
    print(final_message)
    logger.log_event(event_type="battle_end", context=final_message)


def main() -> None:
    parser = argparse.ArgumentParser(description="Orchestrate the war sim and log into greg_notes.db.")
    parser.add_argument("--max-turns", type=int, default=50, help="Maximum number of turns.")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between turns in seconds.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path(__file__).with_name("greg_notes.db"),
        help="Path to greg_notes.db.",
    )
    args = parser.parse_args()

    run_simulation(
        max_turns=args.max_turns,
        delay=args.delay,
        seed=args.seed,
        db_path=args.db_path,
    )


if __name__ == "__main__":
    main()
