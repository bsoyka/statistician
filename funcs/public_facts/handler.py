from random import shuffle

from common.facts import get_static_facts
from common.response import json_response
from common.stats_table import get_public_fun_facts


def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]

    if method != "GET":
        return json_response(405, {"message": "Method not allowed"})

    facts = [
        *get_static_facts(),
        *get_public_fun_facts(),
    ]

    shuffle(facts)

    return json_response(200, {"facts": facts})
