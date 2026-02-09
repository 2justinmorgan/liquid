from typing import (
    List as _List,
    Optional as _Optional,
    cast as _cast,
)
from datetime import (
    datetime as _datetime,
    timedelta as _timedelta,
    date as _date,
)
from src.defines.instrument import (
    TradingHour as _TradingHour,
    WeekdayLiteral as _WeekdayLiteral,
)


class _Day:
    def __init__(
        self,
        start_time: _datetime,
        end_time: _datetime,
        prev_: _Optional["_Day"] = None,
        next_: _Optional["_Day"] = None,
    ) -> None:
        self.start_time: _datetime = start_time
        self.end_time: _datetime = end_time
        self.prev_: _Optional[_Day] = prev_ if prev_ else None
        self.next_: _Optional[_Day] = next_ if next_ else None

    @staticmethod
    def to_day(
        open_date: _date,
        open_th: _TradingHour,
        close_th: _TradingHour,
    ) -> "_Day":
        is_same_day = close_th.week_day == open_th.week_day
        close_date = open_date if is_same_day else open_date + _timedelta(days=1)
        open_dt = _datetime(
            open_date.year,
            open_date.month,
            open_date.day,
            open_th.time.hour,
            open_th.time.minute,
            open_th.time.second,
        )
        close_dt = _datetime(
            close_date.year,
            close_date.month,
            close_date.day,
            close_th.time.hour,
            close_th.time.minute,
            close_th.time.second,
        )
        return _Day(open_dt, close_dt)

class _Week:
    def __init__(self, first_day: _Day) -> None:
        if first_day.prev_ is not None:
            raise ValueError("the head of the list 'days' must be the earliest day of the list")
        num_days: int = 0
        curr_day: _Optional[_Day] = first_day
        while curr_day is not None:
            num_days += 1
            curr_day = curr_day.next_
        self.first_day = first_day
        self.num_days: int = num_days

    @staticmethod
    def _validate_hours(trading_hours: _List[_TradingHour]) -> None:
        if len(trading_hours) <= 0:
            raise ValueError(f"a week must have days")
        num_open = 0
        num_closed = 0
        for trading_hour in trading_hours:
            num_open += 1 if trading_hour.event_type == "SESSION_OPEN" else 0
            if num_open != (num_closed + 1):
                raise ValueError("trading sessions must be open before closing")
            num_closed += 1 if trading_hour.event_type == "SESSION_CLOSE" else 0
        if num_open != num_closed:
            raise ValueError(f"trading sessions must open and close {num_open} != {num_closed}")

    @staticmethod
    def _get_prev_week_indices(
        today: _WeekdayLiteral,
        trading_hours: _List[_TradingHour],
    ) -> _List[int]:
        indices = []
        num_indices = 0
        num_hours = len(trading_hours)
        curr_index = num_hours - 2
        index = 0
        for trading_hour in trading_hours:
            if trading_hour.week_day == today and trading_hour.event_type == "SESSION_OPEN":
                curr_index = index - 2
            index += 1
        while num_indices < (num_hours / 2):
            if curr_index % 2 == 0:
                indices.append(curr_index)
                num_indices += 1
            curr_index -= 1
        return indices

    @staticmethod
    def _get_last_date(week_day: int, curr_date: _date) -> _date:
        current_date = _date(curr_date.year, curr_date.month, curr_date.day) - _timedelta(days=1)
        while current_date.weekday() != week_day:
            current_date -= _timedelta(days=1)
        return current_date

    @staticmethod
    def get_prev_week(now: _datetime, trading_hours: _List[_TradingHour]) -> "_Week":
        _Week._validate_hours(trading_hours)
        curr_weekday: _WeekdayLiteral = _cast(_WeekdayLiteral, [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ][now.weekday()])
        indices = _Week._get_prev_week_indices(curr_weekday, trading_hours)

        head = _Day(now, now)
        curr = head

        for index in indices:
            open_th = trading_hours[index]
            close_th = trading_hours[index + 1]
            open_date = _Week._get_last_date(open_th.week_day_int, now.date())
            prev_ = _Day.to_day(open_date, open_th, close_th)
            prev_.next_ = curr
            curr.prev_ = prev_
            curr = prev_

        if head.prev_:
            head.prev_.next_ = None
        return _Week(curr)
