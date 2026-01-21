import argparse

import re
import sqlite3
import time
from pathlib import Path
from .war_engine import WarEngine




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




def run_simulation(max_turns: int, delay: float, seed: int | None, db_path: Path) -> None:
 
    logger = GregNotesLogger(db_path)
    engine = WarEngine(logger=logger, seed=seed, max_turns=max_turns)
    
    while not engine.is_over():
        logger.set_turn(engine.turn + 1)
        engine.step()
        if delay > 0:
            time.sleep(delay)


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
