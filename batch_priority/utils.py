from datetime import datetime, timedelta


def get_week_range(date):
    # Get the start of the week (Monday)
    start_of_week = date - timedelta(days=date.weekday())
    # Get the end of the week (Sunday)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


def get_start_date_of_week(year, week):
    # Calculate the start date of the week based on the year and week number
    first_day_of_year = datetime(year, 1, 1)
    days_to_add = (week - 1) * 7  # Weeks start from 1
    start_date_of_week = first_day_of_year + timedelta(days=days_to_add)
    # Find Monday for the week
    while start_date_of_week.weekday() != 0:  # 0 = Monday
        start_date_of_week -= timedelta(days=1)
    return start_date_of_week.date()
