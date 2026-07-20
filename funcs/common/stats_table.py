import os
from datetime import datetime, timezone

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
    value: int,
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
        return template.format(value=value)
    except KeyError, ValueError, IndexError:
        return None


def get_public_fun_facts() -> list[str]:
    items = get_public_stats()
    facts: list[str] = []

    for item in items:
        rendered = render_fun_fact(item)
        if rendered:
            facts.append(rendered)

    return facts
