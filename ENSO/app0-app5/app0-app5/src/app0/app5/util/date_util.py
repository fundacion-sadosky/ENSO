from datetime import datetime, timedelta
import pendulum
from typing import Tuple


def now() -> datetime:
    return pendulum.now(tz="America/Buenos_Aires")


def now_minus_days(days: int) -> Tuple[datetime, datetime]:
    dt_tz_to = now()
    dt_tz_from = dt_tz_to.subtract(days=15)

    return dt_tz_from, dt_tz_to


def from_dmy(datetime_str: str) -> datetime:
    parsed_date = pendulum.from_format(datetime_str, "DD/MM/YYYY", tz="America/Buenos_Aires")

    return parsed_date


def from_dmyhm(datetime_str: str) -> datetime:
    parsed_date = pendulum.from_format(datetime_str, "DD/MM/YYYY HH:mm", tz="America/Argentina/Buenos_Aires")

    return parsed_date


def is_today(some_date: datetime) -> bool:
    date_to_check = some_date.date()
    today = datetime.now().date()

    return date_to_check == today


def next_monday(hour: int = 0) -> datetime:
    today = now()
    days_until_next_monday = (7 - today.weekday()) % 7
    next_monday = today + timedelta(days=days_until_next_monday)
    next_monday_at_midnight = next_monday.replace(hour=hour, minute=0, second=0, microsecond=0)
    return next_monday_at_midnight


def to_dmy(the_date: datetime) -> str:
    return the_date.strftime('%d/%m/%Y')


def to_dmyhm(the_date: datetime) -> str:
    return the_date.strftime('%d/%m/%Y %H:%M')


def to_dmyhms(the_date: datetime) -> str:
    return the_date.strftime('%d/%m/%Y %H:%M:%S')


def get_first_and_last_day_of_month(year=None, month=None):
    year = int(year) if year else datetime.now().year
    month = int(month) if month else datetime.now().month
    # Create a datetime object for the first day of the month
    first_day = pendulum.datetime(year, month, 1)

    # Calculate the last day of the month by going to the next month's first day
    # and subtracting one day from it
    if month == 12:
        next_month = pendulum.datetime(year + 1, 1, 1)
    else:
        next_month = pendulum.datetime(year, month + 1, 1)
    last_day = next_month - timedelta(days=1)

    return first_day, last_day
