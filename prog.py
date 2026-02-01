from json import (
    load as _load,
)
from typing import (
    Dict as _Dict,
    List as _List,
    Final as _Final,
    Union as _Union,
)

ACCURACY_DECIMAL: _Final = 6

Instrument = _Dict[str, _Union[str, _List[_Dict[str, str]]]]


class Event:
    def __init__(self, event: _Dict[str, str]) -> None:
        self.open = event["open"]
        self.close = event["close"]
        self.high = event["high"]
        self.low = event["low"]
        self.time = event["time"]

        is_increasing = self.open < self.close
        top_middle = self._get_middle(self.high, self.close if is_increasing else self.open)
        bottom_middle = self._get_middle(self.open if is_increasing else self.close, self.low)
        self.middle = self._get_middle(top_middle, bottom_middle)

    def _get_middle(self, num_a: float, num_b: float) -> float:
        return round((num_a + num_b) / 2, ACCURACY_DECIMAL)


class Day:
    def __init__(self, symbol: str, events: _List[Event]) -> None:
        self.timestamp = events[0].time.split('T')[0]
        self.symbol = symbol
        self.events = events
        self.avg = self._get_avg(events)
        self.len = self._get_len(events)
        self.variance = round(self.len / self.avg, ACCURACY_DECIMAL)
        self.avg_delta = self._get_avg_delta(events)

    def _get_avg(self, events: _List[Event]) -> float:
        total = 0
        for event in events:
            total = round(total + event.middle, ACCURACY_DECIMAL)
        return round(total / len(events), ACCURACY_DECIMAL)

    def _get_len(self, events: _List[Event]) -> float:
        total = 0
        for i in range(1, len(events)):
            total = round(total + abs(events[i - 1].middle - events[i].middle), ACCURACY_DECIMAL)
        return total

    def _get_avg_delta(self, events: _List[Event]) -> float:
        total = 0
        for i in range(1, len(events)):
            diff = abs(events[i - 1].middle - events[i].middle)
            total = round(total + round((diff / events[i - 1].middle) * 100, ACCURACY_DECIMAL), ACCURACY_DECIMAL)
        return round(total / len(events), ACCURACY_DECIMAL)


class Symbol:
    def __init__(self, symbol: str, events: _List[_Dict[str, str]]) -> None:
        self.symbol = symbol
        self.days = self._get_days(events)

    def _get_days(self, events: _List[_Dict[str, str]]) -> _Dict[str, Day]:
        days = {}
        days_with_events = {}
        for event in events:
            timestamp = event["time"]
            day = timestamp.split('T')[0]
            if day not in days_with_events:
                days_with_events[day] = []
            days_with_events[day].append(Event(event))
        for symbol, day_events in days_with_events.items():
            day_events_sorted = day_events #sorted(day_events, key=lambda e: e.time.split('T')[1])
            days[day_events_sorted[0].time.split('T')[0]] = Day(symbol, day_events_sorted)
        return days


class Events:
    def __init__(self, events: _List[_Dict[str, str]]) -> None:
        self.symbols = self._get_symbols(events)

    def _get_symbols(self, events: _List[_Dict[str, str]]) -> _Dict[str, Symbol]:
        symbols = {}
        symbols_all_events = {}
        for event in events:
            symbol = event["symbol"]
            if symbol not in symbols_all_events:
                symbols_all_events[symbol] = []
            symbols_all_events[symbol].append(event)
        for symbol in symbols_all_events:
            symbols[symbol] = Symbol(symbol, symbols_all_events[symbol])
        return symbols


def filter_24_hour_instruments(instruments_all: _List[Instrument]) -> _List[Instrument]:
    instruments = []
    for instrument in instruments_all:
        if "tradingHours" not in instrument:
            continue
        trading_hours = {
            "Sunday": ["", ""],
            "Monday": ["", ""],
            "Tuesday": ["", ""],
            "Wednesday": ["", ""],
            "Thursday": ["", ""],
            "Friday": ["", ""],
            "Saturday": ["", ""],
        }
        for trading_hour in instrument["tradingHours"]:
            day_time = trading_hour["weekDay"].split(',')
            day = day_time[0]
            time = day_time[1]
            index = 0 if trading_hour["eventType"] == "SESSION_OPEN" else 1
            trading_hours[day][index] = time
        is_24_hr = True
        for trading_hour in trading_hours.values():
            if trading_hour[0] != trading_hour[1]:
                if is_24_hr:
                    print(instrument["symbol"], "is not 24hrs", instrument["type"])
                is_24_hr = False
            #if not is_24_hr and trading_hour[0] != "" and trading_hour[1] != "":
            #    print(" ", trading_hour[0], " -", trading_hour[1])
        if is_24_hr:
            print("\t", instrument["symbol"], "is 24hrs", instrument["type"])
            #for trading_hour in trading_hours.values():
            #    print("\t ", trading_hour[0], " -", trading_hour[1])
            instruments.append(instrument)
    return instruments


#mins = _load(open("mins.json", 'r'))
#event = Event(mins["events"][0])
#print(event.high, event.low, event.open, event.close, event.middle)
#events = Events(mins["events"])
#print(events.symbols.keys())
#print("AAPL")
#[print(day.timestamp, day.avg_delta, day.variance) for day in events.symbols["AAPL"].days.values()]
#print("ADAUSD")
#[print(day.timestamp, day.avg_delta, day.variance) for day in events.symbols["ADAUSD"].days.values()]
symbols = _load(open("symbols.json", 'r'))
print(len(filter_24_hour_instruments(symbols["instruments"])))
