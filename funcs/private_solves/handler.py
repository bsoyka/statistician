import json
from datetime import datetime

from common.response import json_response
from common.solves_table import (
    VALID_PENALTIES,
    get_solve_summary,
    list_solves,
    put_solves_batch,
)

SUPPORTED_EVENTS = ("333",)


def validate_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False


def validate_solve_record(record: object) -> str | None:
    if not isinstance(record, dict):
        return "record must be an object"

    event = record.get("event")
    if event not in SUPPORTED_EVENTS:
        return f"event must be one of {SUPPORTED_EVENTS}"

    scramble = record.get("scramble")
    if not isinstance(scramble, str) or not scramble:
        return "scramble must be a non-empty string"

    time_ms = record.get("time_ms")
    if not isinstance(time_ms, int) or time_ms <= 0:
        return "time_ms must be a positive integer"

    penalty = record.get("penalty")
    if penalty not in VALID_PENALTIES:
        return "penalty must be null, '+2', or 'DNF'"

    if not validate_timestamp(record.get("timestamp")):
        return "timestamp must be an ISO 8601 datetime"

    source = record.get("source")
    if not isinstance(source, str) or not source:
        return "source must be a non-empty string"

    return None


def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]
    path = event["requestContext"]["http"]["path"]
    query = event.get("queryStringParameters") or {}

    if method == "POST" and path == "/private/solves/batch":
        try:
            payload = json.loads(event.get("body") or "{}")
        except json.JSONDecodeError:
            return json_response(400, {"message": "Invalid JSON body"})

        records = payload.get("solves")
        if not isinstance(records, list) or not records:
            return json_response(400, {"message": "solves must be a non-empty array"})

        errors = []
        valid = []

        # Validate up front, over the incoming array in order, so that every
        # error carries the caller's own index for it. Writing happens after,
        # in whatever order batching finds convenient.
        for index, record in enumerate(records):
            error = validate_solve_record(record)
            if error:
                errors.append({"index": index, "message": error})
                continue

            valid.append(record)

        imported, skipped = put_solves_batch(valid) if valid else (0, 0)

        return json_response(
            200, {"imported": imported, "skipped": skipped, "errors": errors}
        )

    if method == "GET" and path == "/private/solves":
        solve_event = query.get("event", "333")
        if solve_event not in SUPPORTED_EVENTS:
            return json_response(400, {"message": f"event must be one of {SUPPORTED_EVENTS}"})

        date_from = query.get("from")
        date_to = query.get("to")
        return json_response(
            200,
            {"items": list_solves(solve_event, date_from=date_from, date_to=date_to)},
        )

    if method == "GET" and path == "/private/solves/summary":
        solve_event = query.get("event", "333")
        if solve_event not in SUPPORTED_EVENTS:
            return json_response(400, {"message": f"event must be one of {SUPPORTED_EVENTS}"})

        return json_response(200, get_solve_summary(solve_event))

    return json_response(405, {"message": "Method not allowed"})
