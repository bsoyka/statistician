#!/usr/bin/env python3
"""One-time import of volunteer entries from a CSV file into DynamoDB.

Expected CSV columns (header row required):
  - date         (required) YYYY-MM-DD
  - minutes      (required) positive integer
  - organization (optional)
  - group_name   (optional)
  - notes        (optional)
  - fmsc_meals   (optional) positive integer; only meaningful for FMSC sessions

Usage:
    python scripts/import_volunteer_entries.py entries.csv [--table TABLE] [--region REGION] [--dry-run]

The table name defaults to "statistician-activity-records" and the region to "us-east-1".
"""

import argparse
import csv
import sys
import uuid
from datetime import datetime, timezone


def iso_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def parse_row(row: dict, line_number: int) -> dict:
    errors = []

    date = row.get("date", "").strip()
    if not date:
        errors.append("date is required")
    else:
        try:
            from datetime import date as date_type

            date_type.fromisoformat(date)
        except ValueError:
            errors.append(f"date '{date}' is not a valid YYYY-MM-DD date")

    minutes_raw = row.get("minutes", "").strip()
    if not minutes_raw:
        errors.append("minutes is required")
    else:
        try:
            minutes = int(minutes_raw)
            if minutes <= 0:
                errors.append("minutes must be a positive integer")
        except ValueError:
            errors.append(f"minutes '{minutes_raw}' is not an integer")
            minutes = None

    fmsc_meals = None
    fmsc_meals_raw = row.get("fmsc_meals", "").strip()
    if fmsc_meals_raw:
        try:
            fmsc_meals = int(fmsc_meals_raw)
            if fmsc_meals <= 0:
                errors.append("fmsc_meals must be a positive integer")
                fmsc_meals = None
        except ValueError:
            errors.append(f"fmsc_meals '{fmsc_meals_raw}' is not an integer")

    if errors:
        raise ValueError(f"Row {line_number}: " + "; ".join(errors))

    now = iso_now()
    item = {
        "pk": "ACTIVITY#VOLUNTEER",
        "sk": f"DATE#{date}#ENTRY#{uuid.uuid7()}",
        "entity_type": "volunteer_entry",
        "date": date,
        "minutes": minutes,
        "created_at": now,
        "updated_at": now,
    }

    organization = row.get("organization", "").strip()
    if organization:
        item["organization"] = organization

    group_name = row.get("group_name", "").strip()
    if group_name:
        item["group_name"] = group_name

    notes = row.get("notes", "").strip()
    if notes:
        item["notes"] = notes

    if fmsc_meals is not None:
        item["fmsc_meals"] = fmsc_meals

    return item


def main():
    parser = argparse.ArgumentParser(description="Import volunteer entries from CSV.")
    parser.add_argument("csv_file", help="Path to the CSV file to import")
    parser.add_argument(
        "--table",
        default="statistician-activity-records",
        help="DynamoDB table name (default: statistician-activity-records)",
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region (default: us-east-1)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate the CSV without writing to DynamoDB",
    )
    args = parser.parse_args()

    # Parse and validate all rows before writing anything.
    items = []
    with open(args.csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            print("Error: CSV file is empty or missing a header row.", file=sys.stderr)
            sys.exit(1)

        parse_errors = []
        for line_number, row in enumerate(reader, start=2):  # 1-based, row 1 is header
            try:
                items.append(parse_row(row, line_number))
            except ValueError as e:
                parse_errors.append(str(e))

    if parse_errors:
        print(f"Found {len(parse_errors)} validation error(s):", file=sys.stderr)
        for err in parse_errors:
            print(f"  {err}", file=sys.stderr)
        sys.exit(1)

    print(f"Parsed {len(items)} row(s) successfully.")

    if args.dry_run:
        print("Dry run — no data written.")
        for item in items:
            print(f"  {item}")
        return

    import boto3

    dynamodb = boto3.resource("dynamodb", region_name=args.region)
    table = dynamodb.Table(args.table)

    # Use batch_writer for efficiency; it handles batching in chunks of 25.
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

    print(f"Imported {len(items)} entry/entries into '{args.table}'.")


if __name__ == "__main__":
    main()
