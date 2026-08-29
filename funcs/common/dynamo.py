"""Helpers for DynamoDB reads that can span more than one response page.

DynamoDB caps a single Query or Scan response at 1 MB and reports the cut-off
only through ``LastEvaluatedKey``. A caller that ignores that key silently
returns partial results once a partition outgrows the cap, so every read that
is meant to see the whole range should go through these helpers.
"""


def query_all(table, **kwargs) -> list[dict]:
    """Run a Query, following LastEvaluatedKey until every page is collected."""
    return _collect_pages(table.query, kwargs)


def scan_all(table, **kwargs) -> list[dict]:
    """Run a Scan, following LastEvaluatedKey until every page is collected."""
    return _collect_pages(table.scan, kwargs)


def _collect_pages(operation, kwargs: dict) -> list[dict]:
    items: list[dict] = []

    while True:
        response = operation(**kwargs)
        items.extend(response.get("Items", []))

        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            return items

        kwargs = {**kwargs, "ExclusiveStartKey": last_key}
