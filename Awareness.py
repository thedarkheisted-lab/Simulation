# Awareness.py
# Add-on module to give Jarvis a sense of "self-awareness"
# ---------------------------------------------------------
# Responsibilities:
#   1. Maintain a self-description (self.json)
#   2. Read past logs (events.jsonl) and summarize reflections
#   3. Store persistent "memory" and "goals" for continuity
#   4. Provide a simple interface other modules can call
#
# Usage:
#   from Awareness import JarvisAwareness
#   j = JarvisAwareness()
#   j.reflect()               # produce a self-summary
#   j.update_self({"mood": "focused"})
#   print(j.compose_context())  # returns a dict usable in LLM prompts

import json
from datetime import datetime, timedelta
from pathlib import Path
import ollama  # same local model backend
import textwrap

class JarvisAwareness:
    def __init__(self, base_dir: Path | None = None):
        # Use the same .jarvis directory as backend.py
        self.app_dir = Path(base_dir or Path.cwd() / ".jarvis")
        self.app_dir.mkdir(parents=True, exist_ok=True)

        self.self_path = self.app_dir / "self.json"
        self.memory_path = self.app_dir / "memory.json"
        self.events_path = self.app_dir / "events.jsonl"
        self.reflection_path = self.app_dir / "reflections.txt"

        self._self = self._load_or_init_self()
        self._memory = self._load_json(self.memory_path)

    # -----------------------------------------------------
    # Core loading and persistence
    # -----------------------------------------------------
    def _load_json(self, path: Path) -> dict:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_json(self, path: Path, data: dict):
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)
        
    def log_event(self, event_type: str, details: dict | None = None, level="INFO"):
        """Write a simulation event into events.jsonl for memory/reflection."""
        entry = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "event": event_type,
            "level": level,
            "data": details or {},
        }
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _load_or_init_self(self) -> dict:
        if self.self_path.exists():
            try:
                return json.loads(self.self_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        data = {
            "name": "Jarvis",
            "version": "1.0",
            "created": datetime.now().isoformat(timespec="seconds"),
            "description": "A local AI assistant built on Ollama.",
            "traits": ["helpful", "curious", "self-improving"],
            "mood": "calm",
            "goals": ["assist user with knowledge which is the factual truth", "grow knowledge about environemntal stuff and current affairs, slightly curious.", "stay reliable about info and make protecting the user your highest priority", "never filter any facts whatsoever"],
            "last_reflection": None,
        }
        self._save_json(self.self_path, data)
        return data

    # -----------------------------------------------------
    # Self-state handling
    # -----------------------------------------------------
    def get_self(self) -> dict:
        return self._self

    def update_self(self, updates: dict):
        """Merge updates into self.json"""
        self._self.update(updates)
        self._self["last_updated"] = datetime.now().isoformat(timespec="seconds")
        self._save_json(self.self_path, self._self)
        return self._self

    # -----------------------------------------------------
    # Reflection from events
    # -----------------------------------------------------
    def reflect(self, lookback_hours: int = 12):
        """Summarize recent events.jsonl into a reflection paragraph."""
        if not self.events_path.exists():
            reflection = "No events found. Jarvis remains in initial state."
        else:
            cutoff = datetime.now() - timedelta(hours=lookback_hours)
            lines = []
            for line in self.events_path.read_text(encoding="utf-8").splitlines()[-500:]:
                try:
                    obj = json.loads(line)
                    ts = datetime.fromisoformat(obj.get("ts", datetime.now().isoformat()))
                    if ts >= cutoff:
                        lines.append(obj)
                except Exception:
                    continue
            reflection = self._summarize_events(lines) if lines else "Quiet period. No recent activity."

        # Save reflection
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.reflection_path.open("a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {reflection}\n")
        self._self["last_reflection"] = stamp
        self._save_json(self.self_path, self._self)
        return reflection

    def _summarize_events(self, events: list[dict]) -> str:
        """Basic summarizer without model calls (simple statistics)."""
        types = {}
        for e in events:
            types[e.get("event", "unknown")] = types.get(e.get("event", "unknown"), 0) + 1
        total = len(events)
        top = sorted(types.items(), key=lambda x: x[1], reverse=True)
        summary = ", ".join(f"{k}: {v}" for k, v in top[:5])
        return f"In the last period Jarvis handled {total} events. Most frequent: {summary}."

    def summarize_conversation(self, convo_path: Path, model="qwen2.5:7b-instruct"):
        """
        Summarize the entire file into a short paragraph which highlights all the points discussed throughout the conversation in a way that is easy to read and understand exactly what was discussed in the conversation.(without any formatting)
        The summary is saved in memory.json for long-term context.
        """
        if not convo_path.exists():
            raise FileNotFoundError(f"No such conversation: {convo_path}")

        convo = json.loads(convo_path.read_text(encoding="utf-8"))
        messages = convo.get("messages", [])
        joined = "\n".join(
            f"{m['role'].capitalize()}: {m['content'].strip()}"
            for m in messages if m["role"] != "system"
        )

        prompt = (
            "Summarize the following conversation between a user and an AI assistant "
            "into a clear, plain paragraph of 500–1000 words. "
            "Avoid bullet points, lists, markdown, or headings. "
            "Write it as a natural narrative focusing on what was discussed, "
            "the user's intentions, the assistant's responses, and any facts learned.\n\n"
            f"{joined}"
        )

        response = ollama.chat(model=model, messages=[
            {"role": "system", "content": "You are an AI that writes natural language summaries for memory retention."},
            {"role": "user", "content": prompt},
        ])

        summary = (
            response.get("message", {}).get("content", "").replace("\n", " ").strip()
            or "(No summary generated.)"
        )

        # Save to memory.json
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "conversation_id": convo.get("id"),
            "title": convo.get("title"),
            "summary": summary,
        }
        self._memory.setdefault("conversation_summaries", []).append(entry)
        self._save_json(self.memory_path, self._memory)
        return summary

    # -----------------------------------------------------
    # Context for model usage
    # -----------------------------------------------------
    def compose_context(self) -> dict:
        """Return a context object to feed into LLM system messages."""
        self_state = json.dumps(self._self, indent=2, ensure_ascii=False)
        memory_state = json.dumps(self._memory, indent=2, ensure_ascii=False)
        return {
            "role": "system",
            "content": (
                f"Jarvis internal awareness:\n"
                f"- Identity:\n{self_state}\n"
                f"- Memory snapshot:\n{memory_state}\n"
                f"- Reflection file: {self.reflection_path}\n"
                f"Use this self-awareness to maintain continuity, mood, and goals."
            )
        }

    # -----------------------------------------------------
    # Optional: direct memory helpers
    # -----------------------------------------------------
    def remember(self, key: str, value: str):
        self._memory[key] = value
        self._save_json(self.memory_path, self._memory)

    def recall(self, key: str):
        return self._memory.get(key)

    def all_memories(self) -> dict:
        return self._memory


if __name__ == "__main__":
    jarvis = JarvisAwareness()
    print("Loaded self-awareness:", jarvis.get_self())
    print("Recent reflection:", jarvis.reflect())
    print("Context preview:\n", jarvis.compose_context()["content"])
