from datetime import timedelta


def get_week_range(date):
    # Get the start of the week (Monday)
    start_of_week = date - timedelta(days=date.weekday())
    # Get the end of the week (Sunday)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week
