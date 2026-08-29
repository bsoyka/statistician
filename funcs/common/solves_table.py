import math
import os
from collections import defaultdict

import boto3
from boto3.dynamodb.conditions import Key

from common.dynamo import query_all

_TABLE = boto3.resource("dynamodb").Table(os.environ["ACTIVITY_TABLE"])

VALID_PENALTIES = (None, "+2", "DNF")


def solve_pk(event: str) -> str:
    return f"ACTIVITY#SOLVE#{event}"


def make_solve_sk(timestamp: str) -> str:
    return f"TS#{timestamp}"


def make_solve_item(
    event: str,
    scramble: str,
    time_ms: int,
    penalty: str | None,
    timestamp: str,
    source: str,
) -> dict:
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

    return item


def existing_solve_sks(event: str, timestamps: list[str]) -> set[str]:
    """The sks already stored for `event` that could collide with `timestamps`.

    Only the range actually spanned by `timestamps` is read. sks are
    "TS#" + an ISO 8601 timestamp, so the lexicographic order DynamoDB sorts
    them by is the same one min()/max() use here, and the queried range is
    guaranteed to cover every incoming timestamp.
    """
    key_cond = Key("pk").eq(solve_pk(event)) & Key("sk").between(
        make_solve_sk(min(timestamps)), make_solve_sk(max(timestamps))
    )

    items = query_all(
        _TABLE, KeyConditionExpression=key_cond, ProjectionExpression="sk"
    )
    return {item["sk"] for item in items}


def put_solves_batch(records: list[dict]) -> tuple[int, int]:
    """Write many solve records at once, skipping timestamps already stored.

    Each record is a dict of the fields make_solve_item() takes. Returns
    (written, skipped).

    Records are grouped by event, and each group costs one range Query plus a
    handful of BatchWriteItem calls rather than one conditional put per
    record. BatchWriteItem cannot carry a ConditionExpression, so that Query
    is what keeps a solve whose timestamp is already stored from being
    rewritten; it also means duplicate timestamps *within* `records` have to
    be collapsed here, since BatchWriteItem rejects two writes to the same key
    in one request.
    """
    by_event: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        by_event[record["event"]].append(record)

    items = []
    skipped = 0

    for event, event_records in by_event.items():
        already_stored = existing_solve_sks(
            event, [record["timestamp"] for record in event_records]
        )
        seen: set[str] = set()

        for record in event_records:
            sk = make_solve_sk(record["timestamp"])
            if sk in already_stored or sk in seen:
                skipped += 1
                continue

            seen.add(sk)
            items.append(
                make_solve_item(
                    event=event,
                    scramble=record["scramble"],
                    time_ms=record["time_ms"],
                    penalty=record.get("penalty"),
                    timestamp=record["timestamp"],
                    source=record["source"],
                )
            )

    if items:
        with _TABLE.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    return len(items), skipped


def list_solves(
    event: str, date_from: str | None = None, date_to: str | None = None
) -> list[dict]:
    key_cond = Key("pk").eq(solve_pk(event))

    if date_from and date_to:
        key_cond &= Key("sk").between(
            make_solve_sk(date_from), make_solve_sk(date_to)
        )

    return query_all(_TABLE, KeyConditionExpression=key_cond)


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
