import json
import os

import boto3
from boto3.dynamodb.conditions import Key
from common.stats_table import put_stat

ACTIVITY_TABLE = os.environ["ACTIVITY_TABLE"]
_activity = boto3.resource("dynamodb").Table(ACTIVITY_TABLE)


def recompute_ctl_minutes() -> int:
    response = _activity.query(KeyConditionExpression=Key("pk").eq("ACTIVITY#CTL"))
    items = response.get("Items", [])

    return sum(int(item["minutes"]) for item in items)


def lambda_handler(event, context):
    ctl_minutes = recompute_ctl_minutes()
    ctl_hours = ctl_minutes // 60

    put_stat(
        stat_key="ctl.hours_total",
        value=ctl_hours,
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "ctl_minutes": ctl_minutes,
                "ctl_hours": ctl_hours,
            }
        ),
    }
