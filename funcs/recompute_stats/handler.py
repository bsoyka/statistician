import json
from datetime import datetime, timezone

import boto3
import urllib3
from common.activity_table import list_ctl_weeks, list_volunteer_entries
from common.stats_table import put_stat

_SECRETS_CLIENT = boto3.client("secretsmanager")


def current_year() -> str:
    return str(datetime.now(timezone.utc).year)


def recompute_ctl() -> dict:
    year = current_year()
    year_start = f"{year}-01-01"
    year_end = f"{year}-12-31"

    all_weeks = list_ctl_weeks()
    year_weeks = list_ctl_weeks(date_from=year_start, date_to=year_end)

    total_minutes = sum(int(item["minutes"]) for item in all_weeks)
    year_minutes = sum(int(item["minutes"]) for item in year_weeks)

    put_stat(
        stat_key="volunteering.ctl.hours_total",
        value=total_minutes // 60,
        source="scheduled summary from CTL logs in activity table",
    )
    put_stat(
        stat_key="volunteering.ctl.hours_current_year",
        value=year_minutes // 60,
        source="scheduled summary from CTL logs in activity table",
    )

    return {
        "ctl_total_minutes": total_minutes,
        "ctl_total_hours": total_minutes // 60,
        "ctl_year_minutes": year_minutes,
        "ctl_year_hours": year_minutes // 60,
    }


def recompute_volunteer() -> dict:
    year = current_year()
    year_start = f"{year}-01-01"
    year_end = f"{year}-12-31"

    all_entries = list_volunteer_entries()
    year_entries = list_volunteer_entries(date_from=year_start, date_to=year_end)

    total_minutes = sum(int(e["minutes"]) for e in all_entries)
    year_minutes = sum(int(e["minutes"]) for e in year_entries)

    total_fmsc_meals = sum(
        int(e["fmsc_meals"]) for e in all_entries if "fmsc_meals" in e
    )
    year_fmsc_meals = sum(
        int(e["fmsc_meals"]) for e in year_entries if "fmsc_meals" in e
    )

    put_stat(
        stat_key="volunteering.fmsc.meals_total",
        value=total_fmsc_meals,
        source="scheduled summary from volunteer logs in activity table",
    )
    put_stat(
        stat_key="volunteering.fmsc.meals_current_year",
        value=year_fmsc_meals,
        source="scheduled summary from volunteer logs in activity table",
    )

    return {
        "volunteer_total_minutes": total_minutes,
        "volunteer_total_hours": total_minutes // 60,
        "volunteer_year_minutes": year_minutes,
        "volunteer_year_hours": year_minutes // 60,
        "fmsc_total_meals": total_fmsc_meals,
        "fmsc_year_meals": year_fmsc_meals,
    }


def fetch_unsplash() -> dict:
    secrets_response = _SECRETS_CLIENT.get_secret_value(
        SecretId="statistician/prod/external/unsplash"
    )
    secrets = json.loads(secrets_response["SecretString"])

    unsplash_response = urllib3.request(
        "GET",
        f"https://api.unsplash.com/users/{secrets['username']}/statistics",
        fields={"resolution": "days", "quantity": "7"},
        headers={"Authorization": "Client-ID " + secrets["access_key"]},
    )
    data = unsplash_response.json()

    put_stat(
        stat_key="photography.unsplash.downloads_total",
        value=data["downloads"]["total"],
        source="scheduled request to Unsplash API",
    )
    put_stat(
        stat_key="photography.unsplash.downloads_week",
        value=data["downloads"]["historical"]["change"],
        source="scheduled request to Unsplash API",
    )
    put_stat(
        stat_key="photography.unsplash.views_total",
        value=data["views"]["total"],
        source="scheduled request to Unsplash API",
    )
    put_stat(
        stat_key="photography.unsplash.views_week",
        value=data["views"]["historical"]["change"],
        source="scheduled request to Unsplash API",
    )

    return data


def lambda_handler(event, context):
    ctl = recompute_ctl()
    volunteer = recompute_volunteer()
    unsplash = fetch_unsplash()

    overall_total_hours = ctl["ctl_total_hours"] + volunteer["volunteer_total_hours"]
    overall_year_hours = ctl["ctl_year_hours"] + volunteer["volunteer_year_hours"]

    put_stat(
        stat_key="volunteering.overall.hours_total",
        value=overall_total_hours,
        source="scheduled summary from CTL and volunteer logs in activity table",
    )
    put_stat(
        stat_key="volunteering.overall.hours_current_year",
        value=overall_year_hours,
        source="scheduled summary from CTL and volunteer logs in activity table",
    )

    return {
        "statusCode": 200,
        "body": json.dumps({**ctl, **volunteer, "unsplash_response": unsplash}),
    }
