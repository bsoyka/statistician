import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3

_TABLE_NAME = os.environ["STATS_TABLE"]
_TABLE = boto3.resource("dynamodb").Table(_TABLE_NAME)


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_all_stats() -> list[dict]:
    resp = _TABLE.scan()
    return resp.get("Items", [])


def get_public_stats() -> list[dict]:
    resp = _TABLE.scan(
        FilterExpression="#public = :true",
        ExpressionAttributeNames={"#public": "public"},
        ExpressionAttributeValues={":true": True},
    )
    return resp.get("Items", [])


def get_stat(stat_key: str) -> dict | None:
    resp = _TABLE.get_item(Key={"stat_key": stat_key})
    return resp.get("Item")


def put_stat(
    stat_key: str,
    value: int | Decimal,
    label: str | None = None,
    public: bool | None = None,
    fun_fact_template: str | None = None,
    source: str = "manual",
) -> dict:
    existing = get_stat(stat_key) or {}

    item = {
        "stat_key": stat_key,
        "value": value,
        "label": label if label is not None else existing.get("label", stat_key),
        "public": public if public is not None else existing.get("public", False),
        "source": source,
        "updated_at": iso_now(),
    }

    if fun_fact_template is not None:
        item["fun_fact_template"] = fun_fact_template
    elif "fun_fact_template" in existing:
        item["fun_fact_template"] = existing["fun_fact_template"]

    _TABLE.put_item(Item=item)
    return item


def public_stats_as_nested_object(items: list[dict]) -> dict:
    output: dict = {}

    for item in items:
        stat_key = item["stat_key"]
        value = item["value"]

        current = output
        *parents, leaf = stat_key.split(".")

        for part in parents:
            current = current.setdefault(part, {})

        current[leaf] = value

    return output


def render_fun_fact(item: dict) -> str | None:
    template = item.get("fun_fact_template")
    if not template:
        return None

    value = item.get("value")

    try:
        return template.format_map(_ExpressionMap(value))
    except KeyError, ValueError, IndexError, ZeroDivisionError, SyntaxError:
        return None


class _ExpressionMap:
    """Mapping that evaluates simple arithmetic expressions against `value`.

    Allows format strings like ``{value:,}`` or ``{value/365:,.0f}``.
    The key is evaluated as a Python expression with ``value`` in scope,
    so any valid numeric expression referencing ``value`` will work.
    """

    def __init__(self, value: object) -> None:
        self._value = value

    def __getitem__(self, key: str) -> object:
        return eval(key, {"__builtins__": {}}, {"value": self._value})  # noqa: S307

    def __contains__(self, key: object) -> bool:
        try:
            self[key]  # type: ignore[arg-type]
            return True
        except Exception:
            return False


def get_public_fun_facts() -> list[str]:
    items = get_public_stats()
    facts: list[str] = []

    for item in items:
        rendered = render_fun_fact(item)
        if rendered:
            facts.append(rendered)

    return facts
