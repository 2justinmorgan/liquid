from typing import (
    Dict as _Dict,
    Union as _Union,
    List as _List,
    Literal as _Literal,
)
from time import sleep
from os import path
from datetime import (
    datetime as _datetime,
    timezone as _timezone,
    timedelta as _timedelta,
)
from json import (
    load as _load,
    dumps as _dumps,
    dump as _dump,
)
from src.liquid import get_market_data
from src.defines.event_type import EventType
from src.defines.date_time import DateTime
from src.enums.symbols import Symbol

Weekday = _Literal[
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]
EventTypeName = _Literal[
    "SESSION_OPEN",
    "SESSION_CLOSE",
]


class Session:
    def __init__(self, trading_hour: _Dict[str, str], today: _datetime) -> None:
        week_day_split = trading_hour["weekDay"].split(',')
        self.weekday: str = week_day_split[0]
        self.time: str = week_day_split[1].strip()
        self.num_days_ago = get_num_days_past(self.weekday)
        day = (today - _timedelta(days=self.num_days_ago)).date()
        self.dt = _datetime.fromisoformat(f"{day}T{self.time}")


def get_events(symbol: Symbol, start_time: _datetime, end_time: _datetime) -> None:
    if path.isfile("out/" + get_fname(symbol, start_time, end_time)):
        print("file exists")
        return
    sleep(2)
    response = get_market_data(
        [symbol],
        [EventType(
            "Candle",
            "m",
            DateTime._from_datetime(start_time),
            DateTime._from_datetime(end_time),
        )],
    )
    if "events" not in response:
        return []
    return response["events"]


from datetime import datetime, timezone

def get_num_days_past(weekday: Weekday) -> int:
    weekday_map = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    
    target_idx = weekday_map.index(weekday)
    today_idx = datetime.now(tz=timezone.utc).weekday()
    diff = (today_idx - target_idx) % 7
    
    return diff if diff > 0 else 7


def get_fname(symbol, from_dt, to_dt) -> str:
    return f"_{symbol}_{from_dt.date()}_{to_dt.date()}.json"


def write_to_file(symbol, from_dt, to_dt, events):
    fname = get_fname(symbol, from_dt, to_dt)
    _dump(events, open(f"out/{fname}", 'w'))


def get_events_without_hours(symbol: Symbol, today: _datetime):
    for i in range(1, 7):
        date = today.date() - _timedelta(days=i)
        from_dt = _datetime.fromisoformat(f"{date}T00:00:00Z")
        to_dt = _datetime.fromisoformat(f"{date}T23:59:00Z")
        events = get_events(
            symbol,
            from_dt,
            to_dt,
        )
        if len(events) <= 0:
            print("NOPE", symbol)
            return
        write_to_file(symbol, from_dt, to_dt, events)


def get_events_with_hours(symbol: Symbol, trading_hours: _List[_Dict[str, str]], today: _datetime):
    assert len(trading_hours) % 2 == 0
    for i in range(0, len(trading_hours), 2):
        session_open = Session(trading_hours[i], today)
        session_close = Session(trading_hours[i + 1], today)
        events = get_events(
            symbol,
            session_open.dt,
            session_close.dt,
        )
        if len(events) <= 0:
            print("NOPE", symbol)
            return
        write_to_file(symbol, session_open.dt, session_close.dt, events)


instruments = _load(open("instruments.json", 'r'))
for instrument in instruments:
    today = _datetime.now(tz=_timezone.utc)
    symbol = instrument["symbol"]
    if instrument.get("currency") != "USD":
        continue
    if "tradingHours" not in instrument:
        events = get_events_without_hours(symbol, today)
        continue
    events = get_events_with_hours(symbol, instrument["tradingHours"][2:], today)
