import datetime


def iterdays(start, end):
    delta = (end - start).days + 1
    return (start + datetime.timedelta(n) for n in range(delta))


def itermonths(start, end):
    start_month = start.year * 12 + start.month - 1
    end_month = end.year * 12 + end.month
    for year_month in range(start_month, end_month):
        year, month = divmod(year_month, 12)
        yield datetime.date(year, month + 1, 1)


def iteryears(start, end):
    for year in range(start.year, end.year + 1):
        yield datetime.date(year, 1, 1)


def _first_day_of_week(date):
    year, week, weekday = date.isocalendar()
    return date - datetime.timedelta(days=weekday-1)


def _byweek(start, end):
    # monday before 'start'
    start = _first_day_of_week(start)

    # monday before 'end'
    end = _first_day_of_week(end)

    delta = (end - start).days

    return start, end, delta


def iterweeks(start, end):
    start, end, delta = _byweek(start, end)
    for n in range(0, delta, 7):
        yield start + datetime.timedelta(n)


def numweeks(start, end):
    start, end, delta = _byweek(start, end)
    return len(range(0, delta, 7))


def nummonths(start, end):
    return (end.year - start.year) * 12 + end.month - start.month
