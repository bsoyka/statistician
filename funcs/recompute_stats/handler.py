import os
from datetime import datetime, timezone

import boto3

ACTIVITY_TABLE = os.environ["ACTIVITY_TABLE"]
STATS_TABLE = os.environ["STATS_TABLE"]

_activity = boto3.resource("dynamodb").Table(ACTIVITY_TABLE)
_stats = boto3.resource("dynamodb").Table(STATS_TABLE)


def iso_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def recompute_ctl_minutes() -> int:
    response = _activity.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("pk").eq("ACTIVITY#CTL")
    )
    items = response.get("Items", [])
    return sum(int(item["minutes"]) for item in items)


def upsert_stat(key: str, value: float, label: str) -> None:
    now = iso_now()
    _stats.put_item(
        Item={
            "key": key,
            "value": value,
            "label": label,
            "updated_at": now,
        }
    )


def lambda_handler(event, context):
    ctl_minutes = recompute_ctl_minutes()
    ctl_hours = ctl_minutes / 60.0

    upsert_stat(
        key="volunteering.ctl.hours_total",
        value=ctl_hours,
        label="Crisis Text Line volunteer hours",
    )

    return {
        "statusCode": 200,
        "body": {
            "ctl_minutes": ctl_minutes,
            "ctl_hours": ctl_hours,
        },
    }
