import json
from importlib.resources import files


def get_static_facts() -> list[str]:
    raw = (files("common") / "static_facts.json").read_text(encoding="utf-8")
    data = json.loads(raw)

    return [fact for fact in data if isinstance(fact, str) and fact.strip()]
