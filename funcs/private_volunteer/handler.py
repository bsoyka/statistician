import json
from datetime import date as date_type

from common.response import json_response
from common.volunteer_table import create_entry, get_summary, list_entries


def validate_date(value: str) -> bool:
    try:
        date_type.fromisoformat(value)
        return True
    except ValueError:
        return False


def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]
    path = event["requestContext"]["http"]["path"]
    query = event.get("queryStringParameters") or {}

    if method == "POST" and path == "/private/volunteer/entries":
        try:
            payload = json.loads(event.get("body") or "{}")
        except json.JSONDecodeError:
            return json_response(400, {"message": "Invalid JSON body"})

        date = payload.get("date")
        minutes = payload.get("minutes")
        organization = payload.get("organization")
        group_name = payload.get("group_name")
        notes = payload.get("notes")

        if not isinstance(date, str) or not validate_date(date):
            return json_response(
                400, {"message": "date must be an ISO date (YYYY-MM-DD)"}
            )

        if not isinstance(minutes, int) or minutes <= 0:
            return json_response(400, {"message": "minutes must be a positive integer"})

        item = create_entry(
            date=date,
            minutes=minutes,
            organization=organization,
            group_name=group_name,
            notes=notes,
        )
        return json_response(201, item)

    if method == "GET" and path == "/private/volunteer/entries":
        date_from = query.get("from")
        date_to = query.get("to")

        if date_from and not validate_date(date_from):
            return json_response(400, {"message": "from must be YYYY-MM-DD"})
        if date_to and not validate_date(date_to):
            return json_response(400, {"message": "to must be YYYY-MM-DD"})

        return json_response(
            200, {"items": list_entries(date_from=date_from, date_to=date_to)}
        )

    if method == "GET" and path == "/private/volunteer/summary":
        date_from = query.get("from")
        date_to = query.get("to")

        if date_from and not validate_date(date_from):
            return json_response(400, {"message": "from must be YYYY-MM-DD"})
        if date_to and not validate_date(date_to):
            return json_response(400, {"message": "to must be YYYY-MM-DD"})

        return json_response(200, get_summary(date_from=date_from, date_to=date_to))

    return json_response(405, {"message": "Method not allowed"})
