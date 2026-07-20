from common.response import json_response
from common.stats_table import get_public_stats, get_stat, public_stats_as_nested_object


def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]
    path_params = event.get("pathParameters") or {}

    if method != "GET":
        return json_response(405, {"message": "Method not allowed"})

    stat_key = path_params.get("key")
    if stat_key:
        item = get_stat(stat_key)
        if not item or not item.get("public", False):
            return json_response(404, {"message": "Stat not found"})
        return json_response(200, item)

    items = sorted(get_public_stats(), key=lambda i: i["stat_key"])
    return json_response(200, public_stats_as_nested_object(items))
