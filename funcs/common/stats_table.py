import os
from datetime import datetime, timezone

import boto3

_TABLE_NAME = os.environ["STATS_TABLE"]
_TABLE = boto3.resource("dynamodb").Table(_TABLE_NAME)


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    label: str | None,
    public: bool | None,
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

    _TABLE.put_item(Item=item)
    return item
