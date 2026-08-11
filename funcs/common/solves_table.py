import math
import os

import boto3
from boto3.dynamodb.conditions import Key

_TABLE = boto3.resource("dynamodb").Table(os.environ["ACTIVITY_TABLE"])

VALID_PENALTIES = (None, "+2", "DNF")


def solve_pk(event: str) -> str:
    return f"ACTIVITY#SOLVE#{event}"


def make_solve_sk(timestamp: str) -> str:
    return f"TS#{timestamp}"


def put_solve_if_new(
    event: str,
    scramble: str,
    time_ms: int,
    penalty: str | None,
    timestamp: str,
    source: str,
) -> bool:
    """Write a solve record, skipping it silently if the timestamp already exists.

    Returns True if the record was written, False if it was a duplicate.
    """
    item = {
        "pk": solve_pk(event),
        "sk": make_solve_sk(timestamp),
        "entity_type": "cube_solve",
        "event": event,
        "scramble": scramble,
        "time_ms": time_ms,
        "timestamp": timestamp,
        "source": source,
    }
    if penalty is not None:
        item["penalty"] = penalty

    try:
        _TABLE.put_item(Item=item, ConditionExpression="attribute_not_exists(sk)")
        return True
    except _TABLE.meta.client.exceptions.ConditionalCheckFailedException:
        return False


def list_solves(
    event: str, date_from: str | None = None, date_to: str | None = None
) -> list[dict]:
    key_cond = Key("pk").eq(solve_pk(event))

    if date_from and date_to:
        key_cond &= Key("sk").between(
            make_solve_sk(date_from), make_solve_sk(date_to)
        )

    response = _TABLE.query(KeyConditionExpression=key_cond)
    return response.get("Items", [])


def effective_time_ms(item: dict) -> int | None:
    """Time that counts toward PRs and averages: None for a DNF, +2000ms for a +2."""
    penalty = item.get("penalty")
    if penalty == "DNF":
        return None

    time_ms = int(item["time_ms"])
    if penalty == "+2":
        return time_ms + 2000
    return time_ms


def compute_rolling_average(items: list[dict], window: int) -> int | None:
    """WCA-style rolling average of the most recent `window` solves, in ms.

    `items` must be sorted chronologically ascending (oldest first). Per WCA
    convention, the best and worst results in the window are trimmed before
    averaging. A single DNF counts as the window's worst result and is
    trimmed away like any other outlier; two or more DNFs make the whole
    average a DNF (returned as None), as does not having `window` solves yet.
    """
    if len(items) < window:
        return None

    recent = items[-window:]
    dnf_count = sum(1 for item in recent if item.get("penalty") == "DNF")
    if dnf_count >= 2:
        return None

    times = sorted(
        effective_time_ms(item) if effective_time_ms(item) is not None else math.inf
        for item in recent
    )
    trimmed = times[1:-1]
    if any(math.isinf(t) for t in trimmed):
        return None

    return round(sum(trimmed) / len(trimmed))


def get_solve_summary(event: str) -> dict:
    items = list_solves(event)

    valid_times = [
        effective_time_ms(item)
        for item in items
        if effective_time_ms(item) is not None
    ]

    return {
        "count_total": len(items),
        "pr_single_ms": min(valid_times) if valid_times else None,
        "current_ao5_ms": compute_rolling_average(items, 5),
        "current_ao12_ms": compute_rolling_average(items, 12),
    }
