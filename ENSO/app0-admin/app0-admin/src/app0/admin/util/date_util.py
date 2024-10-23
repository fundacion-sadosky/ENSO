from datetime import datetime, timedelta
import pendulum
from typing import Tuple


def now() -> datetime:
    # dt = datetime.now()
    # dt_tz = pendulum.instance(dt).in_timezone('UTC')

    # return datetime.fromisoformat(dt_tz.to_iso8601_string().replace('Z', '+00:00'))
    return pendulum.now(tz="America/Buenos_Aires")


def now_minus_days(days: int) -> Tuple[datetime, datetime]:
    # dt = datetime.now()
    # dt_tz_to = pendulum.instance(dt).in_timezone('UTC')
    # dt_tz_from = dt_tz_to.subtract(days=15)
    dt_tz_to = now()
    dt_tz_from = dt_tz_to.subtract(days=15)

    # dt_to = datetime.fromisoformat(dt_tz_to.to_iso8601_string().replace('Z', '+00:00'))
    # dt_from = datetime.fromisoformat(dt_tz_from.to_iso8601_string().replace('Z', '+00:00'))
    # return dt_from, dt_to
    return dt_tz_from, dt_tz_to


def from_dmy(datetime_str: str) -> datetime:
    # dt = datetime.strptime(datetime_str, '%d/%m/%Y')
    # dt_tz = pendulum.instance(dt).in_timezone('UTC')

    # return datetime.fromisoformat(dt_tz.to_iso8601_string().replace('Z', '+00:00'))
    parsed_date = pendulum.from_format(datetime_str, "DD/MM/YYYY", tz="America/Buenos_Aires")

    return parsed_date


def from_dmyhm(datetime_str: str) -> datetime:
    # dt = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M')
    # dt_tz = pendulum.instance(dt).in_timezone('UTC')

    # return datetime.fromisoformat(dt_tz.to_iso8601_string().replace('Z', '+00:00'))
    parsed_date = pendulum.from_format(datetime_str, "DD/MM/YYYY HH:mm", tz="America/Argentina/Buenos_Aires")

    return parsed_date


def is_today(some_date: datetime) -> bool:
    date_to_check = some_date.date()
    today = datetime.now().date()

    return date_to_check == today


def next_monday() -> datetime:
    today = now()
    days_until_next_monday = (7 - today.weekday()) % 7
    next_monday = today + timedelta(days=days_until_next_monday)
    next_monday_at_midnight = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
    return next_monday_at_midnight
