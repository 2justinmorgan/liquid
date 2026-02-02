from json import (
    load as _load,
)
from typing import (
    Dict as _Dict,
    List as _List,
    Final as _Final,
    Union as _Union,
)
from pathlib import Path as _Path
from datetime import (
    datetime as _datetime,
    timedelta as _timedelta,
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


class Sequence:
    def __init__(self, symbol: str, events: _List[Event]) -> None:
        self.timestamp = events[0].time.split('T')[0]
        self.symbol = symbol
        self.events = events
        self.avg = self._get_avg(events)
        self.len = self._get_len(events)
        self.variance = round(self.len / self.avg, ACCURACY_DECIMAL)
        self.avg_delta = self._get_avg_delta(events)
        self._is_contiguous = self._is_contiguous(events)

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

    def _is_contiguous(self, events: _List[Event]) -> bool:
        for i in range(1, len(events)):
            dt_prev = _datetime.strptime(events[i - 1].time, "%Y-%m-%dT%H:%M:%Sz")
            dt_curr = _datetime.strptime(events[i].time, "%Y-%m-%dT%H:%M:%Sz")
            if (dt_prev + _timedelta(seconds=1)) != dt_curr:
                #print(self.symbol, self.timestamp, "NOT contiguous:", dt_prev, dt_curr)
                return False
        #print(self.symbol, self.timestamp, "is contiguous")
        return True


class Symbol:
    def __init__(self, symbol: str, events: _List[_Dict[str, str]]) -> None:
        self.symbol = symbol
        self.seqs = self._get_seqs(events)

        deltas_sum = 0
        delta_min = None
        delta_max = 0
        for seq in self.seqs.values():
            deltas_sum += round(seq.avg_delta, ACCURACY_DECIMAL)
            delta_min = round(seq.avg_delta if delta_min is None or seq.avg_delta < delta_min else delta_min, ACCURACY_DECIMAL)
            delta_max = round(seq.avg_delta if seq.avg_delta > delta_max else delta_max, ACCURACY_DECIMAL)
        self.avg_delta = round(deltas_sum / len(self.seqs), ACCURACY_DECIMAL)
        self.low_delta = delta_min
        self.high_delta = delta_max
        self.range_dist = round(abs(self.high_delta - self.low_delta), ACCURACY_DECIMAL)

    def _to_dt(self, timestamp: str) -> _datetime:
        return _datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%Sz")

    def _get_seqs(self, events: _List[_Dict[str, str]]) -> _Dict[str, Sequence]:
        seqs = {}
        seqs_with_events = {}
        seq_key = events[0]["time"]
        for i in range(1, len(events)):
            dt_prev = self._to_dt(events[i - 1]["time"])
            dt_curr = self._to_dt(events[i]["time"])
            if (dt_prev + _timedelta(minutes=1)) != dt_curr:
                seq_key = events[i]["time"]
            if seq_key not in seqs_with_events:
                seqs_with_events[seq_key] = []
            seqs_with_events[seq_key].append(Event(events[i]))
        for seq_events in seqs_with_events.values():
            if len(seq_events) < 2:
                continue
            seq_events_sorted = seq_events #sorted(seq_events, key=lambda e: e.time.split('T')[1])
            seqs[seq_events_sorted[0].time] = Sequence(self.symbol, seq_events_sorted)
        return seqs

    def output_details(self) -> None:
        print(f"{self.avg_delta:.6f}", f"\t{self.low_delta:.6f}-{self.high_delta:.6f}:{self.range_dist:.6f}" "\tnum-seqs:", len(self.seqs), f"\tsymbol:{self.symbol:11}")


class Events:
    def __init__(self, events: _List[_Dict[str, str]]) -> None:
        self.symbols = self._get_symbols(events)
        self.sorted_keys = sorted(self.symbols.keys(), key=lambda sym: self.symbols[sym].avg_delta, reverse=True)

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

    def output_details(self) -> None:
        for symbol in self.sorted_keys:
            self.symbols[symbol].output_details()


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
                    print(instrument["symbol"], "is not 24hrs", instrument["type"], instrument["currency"], instrument["description"])
                is_24_hr = False
        if is_24_hr:
            print(f"\t", instrument["symbol"], "is 24hrs", instrument["type"], instrument["currency"], instrument["description"])
            instruments.append(instrument)
    return instruments


def analyze_files() -> None:
    dir_path = _Path("out/")
    files_list = [p for p in dir_path.iterdir() if p.is_file()]
    events = []

    for file_path in files_list:
        file_name = str(file_path).split('\\')[1]
        #print(f"'out/{file_name}'")
        with open(f"out/{file_name}", 'r') as file_obj:
            for event in _load(file_obj):
                events.append(event)
    return Events(events)
