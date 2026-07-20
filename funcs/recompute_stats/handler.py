import json
from datetime import datetime, timezone

from common.activity_table import list_ctl_weeks, list_volunteer_entries
from common.stats_table import put_stat


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
        stat_key="volunteering.overall.hours_total",
        value=total_minutes // 60,
        source="scheduled summary from volunteer logs in activity table",
    )
    put_stat(
        stat_key="volunteering.overall.hours_current_year",
        value=year_minutes // 60,
        source="scheduled summary from volunteer logs in activity table",
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


def lambda_handler(event, context):
    ctl = recompute_ctl()
    volunteer = recompute_volunteer()

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
        "body": json.dumps({**ctl, **volunteer}),
    }
