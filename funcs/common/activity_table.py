import os
import uuid
from datetime import date as date_type
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

_TABLE = boto3.resource("dynamodb").Table(os.environ["ACTIVITY_TABLE"])


def iso_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def is_sunday(value: str) -> bool:
    return date_type.fromisoformat(value).weekday() == 6


def make_volunteer_sk(entry_date: str) -> str:
    return f"DATE#{entry_date}#ENTRY#{uuid.uuid7()}"


def iso_week_string(date_value: str) -> str:
    d = date_type.fromisoformat(date_value)
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def volunteer_pk() -> str:
    return "ACTIVITY#VOLUNTEER"


def ctl_pk() -> str:
    return "ACTIVITY#CTL"


def ctl_week_sk(week_end_date: str) -> str:
    return f"WEEK_END#{week_end_date}"


def create_volunteer_entry(
    date: str,
    minutes: int,
    organization: str | None = None,
    group_name: str | None = None,
    notes: str | None = None,
) -> dict:
    now = iso_now()
    item = {
        "pk": volunteer_pk(),
        "sk": make_volunteer_sk(date),
        "entity_type": "volunteer_entry",
        "date": date,
        "minutes": minutes,
        "created_at": now,
        "updated_at": now,
    }

    if organization:
        item["organization"] = organization
    if group_name:
        item["group_name"] = group_name
    if notes:
        item["notes"] = notes

    _TABLE.put_item(Item=item)
    return item


def list_volunteer_entries(
    date_from: str | None = None, date_to: str | None = None
) -> list[dict]:
    if date_from and date_to:
        response = _TABLE.query(
            KeyConditionExpression=Key("pk").eq(volunteer_pk())
            & Key("sk").between(
                f"DATE#{date_from}#",
                f"DATE#{date_to}#~",
            )
        )
    else:
        response = _TABLE.query(KeyConditionExpression=Key("pk").eq(volunteer_pk()))

    return response.get("Items", [])


def create_or_update_ctl_week(
    week_end_date: str,
    minutes: int,
    people_helped: int,
    notes: str | None = None,
) -> dict:
    now = iso_now()
    key = {"pk": ctl_pk(), "sk": ctl_week_sk(week_end_date)}

    existing = _TABLE.get_item(Key=key).get("Item")

    item = {
        "pk": ctl_pk(),
        "sk": ctl_week_sk(week_end_date),
        "entity_type": "ctl_week",
        "week_end_date": week_end_date,
        "minutes": minutes,
        "people_helped": people_helped,
        "created_at": existing.get("created_at", now) if existing else now,
        "updated_at": now,
    }

    if notes:
        item["notes"] = notes

    _TABLE.put_item(Item=item)
    return item


def list_ctl_weeks(
    date_from: str | None = None, date_to: str | None = None
) -> list[dict]:
    if date_from and date_to:
        response = _TABLE.query(
            KeyConditionExpression=Key("pk").eq(ctl_pk())
            & Key("sk").between(
                f"WEEK_END#{date_from}",
                f"WEEK_END#{date_to}",
            )
        )
    else:
        response = _TABLE.query(KeyConditionExpression=Key("pk").eq(ctl_pk()))

    return response.get("Items", [])
