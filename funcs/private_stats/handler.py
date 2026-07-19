import json

from common.response import json_response
from common.stats_table import get_all_stats, get_stat, put_stat


def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]
    path_params = event.get("pathParameters") or {}

    if method == "GET":
        stat_key = path_params.get("key")
        if stat_key:
            item = get_stat(stat_key)
            if not item:
                return json_response(404, {"message": "Stat not found"})
            return json_response(200, item)

        return json_response(200, {"items": get_all_stats()})

    if method == "PUT":
        stat_key = path_params.get("key")
        if not stat_key:
            return json_response(400, {"message": "Missing stat key"})

        try:
            payload = json.loads(event.get("body") or "{}")
        except json.JSONDecodeError:
            return json_response(400, {"message": "Invalid JSON body"})

        value = payload.get("value")
        label = payload.get("label")
        public = payload.get("public")
        fun_fact_template = payload.get("fun_fact_template")

        if not isinstance(value, int):
            return json_response(400, {"message": "value must be an integer"})

        item = put_stat(
            stat_key=stat_key,
            value=value,
            label=label,
            public=public,
            fun_fact_template=fun_fact_template,
        )
        return json_response(200, item)

    return json_response(405, {"message": "Method not allowed"})
