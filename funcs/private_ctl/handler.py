import json
from datetime import date as date_type

from common.activity_table import list_ctl_weeks, upsert_ctl_week
from common.response import json_response


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

    # PUT /private/ctl/weeks/{week_end_date}
    if method == "PUT" and path.startswith("/private/ctl/weeks/"):
        week_end_date = path.split("/private/ctl/weeks/")[1]

        if not validate_date(week_end_date):
            return json_response(400, {"message": "week_end_date must be YYYY-MM-DD"})

        try:
            payload = json.loads(event.get("body") or "{}")
        except json.JSONDecodeError:
            return json_response(400, {"message": "Invalid JSON body"})

        minutes = payload.get("minutes")
        people_helped = payload.get("people_helped")
        notes = payload.get("notes")

        if not isinstance(minutes, int) or minutes < 0:
            return json_response(
                400, {"message": "minutes must be a non-negative integer"}
            )

        if not isinstance(people_helped, int) or people_helped < 0:
            return json_response(
                400, {"message": "people_helped must be a non-negative integer"}
            )

        item = upsert_ctl_week(
            week_end_date=week_end_date,
            minutes=minutes,
            people_helped=people_helped,
            notes=notes,
        )
        return json_response(200, item)

    # GET /private/ctl/weeks?from=YYYY-MM-DD&to=YYYY-MM-DD
    if method == "GET" and path == "/private/ctl/weeks":
        date_from = query.get("from")
        date_to = query.get("to")

        if date_from and not validate_date(date_from):
            return json_response(400, {"message": "from must be YYYY-MM-DD"})
        if date_to and not validate_date(date_to):
            return json_response(400, {"message": "to must be YYYY-MM-DD"})

        return json_response(
            200, {"items": list_ctl_weeks(date_from=date_from, date_to=date_to)}
        )

    # GET /private/ctl/summary?from=YYYY-MM-DD&to=YYYY-MM-DD
    if method == "GET" and path == "/private/ctl/summary":
        date_from = query.get("from")
        date_to = query.get("to")

        if date_from and not validate_date(date_from):
            return json_response(400, {"message": "from must be YYYY-MM-DD"})
        if date_to and not validate_date(date_to):
            return json_response(400, {"message": "to must be YYYY-MM-DD"})

        items = list_ctl_weeks(date_from=date_from, date_to=date_to)
        total_minutes = sum(int(item["minutes"]) for item in items)
        total_people_helped = sum(int(item["people_helped"]) for item in items)

        return json_response(
            200,
            {
                "total_minutes": total_minutes,
                "total_hours": total_minutes / 60,
                "total_people_helped": total_people_helped,
                "week_count": len(items),
            },
        )

    return json_response(405, {"message": "Method not allowed"})
