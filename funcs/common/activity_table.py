import os
import uuid
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


def volunteer_pk() -> str:
    return "ACTIVITY#VOLUNTEER"


def make_volunteer_sk(entry_date: str) -> str:
    return f"DATE#{entry_date}#ENTRY#{uuid.uuid7()}"


def create_volunteer_entry(
    date: str,
    minutes: int,
    organization: str | None = None,
    group_name: str | None = None,
    notes: str | None = None,
    fmsc_meals: int | None = None,
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
    if fmsc_meals is not None:
        item["fmsc_meals"] = fmsc_meals

    _TABLE.put_item(Item=item)
    return item


def list_volunteer_entries(
    date_from: str | None = None, date_to: str | None = None
) -> list[dict]:
    key_cond = Key("pk").eq(volunteer_pk())

    if date_from and date_to:
        key_cond &= Key("sk").between(f"DATE#{date_from}#", f"DATE#{date_to}#~")

    response = _TABLE.query(KeyConditionExpression=key_cond)
    return response.get("Items", [])


def get_volunteer_summary(
    date_from: str | None = None, date_to: str | None = None
) -> dict:
    items = list_volunteer_entries(date_from=date_from, date_to=date_to)
    total_minutes = sum(int(item["minutes"]) for item in items)
    total_fmsc_meals = sum(
        int(item["fmsc_meals"]) for item in items if "fmsc_meals" in item
    )

    summary: dict = {
        "total_minutes": total_minutes,
        "total_hours": total_minutes // 60,
        "entry_count": len(items),
    }

    if total_fmsc_meals:
        summary["total_fmsc_meals"] = total_fmsc_meals

    return summary


def ctl_pk() -> str:
    return "ACTIVITY#CTL"


def ctl_week_sk(week_end_date: str) -> str:
    return f"WEEK_END#{week_end_date}"


def upsert_ctl_week(
    week_end_date: str,
    minutes: int,
    notes: str | None = None,
) -> dict:
    now = iso_now()
    pk = ctl_pk()
    sk = ctl_week_sk(week_end_date)

    existing = _TABLE.get_item(Key={"pk": pk, "sk": sk}).get("Item")

    if existing:
        update_expr = "SET minutes = :minutes, updated_at = :updated_at"
        expr_values = {
            ":minutes": minutes,
            ":updated_at": now,
        }

        if notes is not None:
            update_expr += ", notes = :notes"
            expr_values[":notes"] = notes

        _TABLE.update_item(
            Key={"pk": pk, "sk": sk},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values,
        )
    else:
        item = {
            "pk": pk,
            "sk": sk,
            "entity_type": "ctl_week",
            "week_end_date": week_end_date,
            "minutes": minutes,
            "created_at": now,
            "updated_at": now,
        }

        if notes is not None:
            item["notes"] = notes

        _TABLE.put_item(Item=item)

    return _TABLE.get_item(Key={"pk": pk, "sk": sk})["Item"]


def list_ctl_weeks(
    date_from: str | None = None, date_to: str | None = None
) -> list[dict]:
    key_cond = Key("pk").eq(ctl_pk())

    if date_from and date_to:
        key_cond &= Key("sk").between(f"WEEK_END#{date_from}", f"WEEK_END#{date_to}")

    response = _TABLE.query(KeyConditionExpression=key_cond)
    return response.get("Items", [])
