from datetime import (
    datetime as _datetime,
	timezone as _timezone,
	timedelta as _timedelta,
)
from typing import (
    Literal as _Literal,
    Optional as _Optional,
    Union as _Union,
)


_YEAR = _Literal["2026", "2025", "2024"]
_MONTH = _Literal[
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
]
_DAY = _Literal[
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "29",
    "30",
    "31",
]
_HOUR = _Literal[
     "00",
     "01",
     "02",
     "03",
     "04",
     "05",
     "06",
     "07",
     "08",
     "09",
     "10",
     "11",
     "12",
     "13",
     "14",
     "15",
     "16",
     "17",
     "18",
     "19",
     "20",
     "21",
     "22",
     "23",
]
_MINUTE = _Literal[
     "00",
     "01",
     "02",
     "03",
     "04",
     "05",
     "06",
     "07",
     "08",
     "09",
     "10",
     "11",
     "12",
     "13",
     "14",
     "15",
     "16",
     "17",
     "18",
     "19",
     "20",
     "21",
     "22",
     "23",
     "24",
     "25",
     "26",
     "27",
     "28",
     "29",
     "30",
     "31",
     "32",
     "33",
     "34",
     "35",
     "36",
     "37",
     "38",
     "39",
     "40",
     "41",
     "42",
     "43",
     "44",
     "45",
     "46",
     "47",
     "48",
     "49",
     "50",
     "51",
     "52",
     "53",
     "54",
     "55",
     "56",
     "57",
     "58",
     "59",
]
_SECOND = _MINUTE


class DateTime:
    def __init__(
        self,
        year: _YEAR,
        month: _MONTH,
        day: _DAY,
        hour: _HOUR,
        minute: _MINUTE,
        second: _SECOND,
    ) -> None:
        month_int = {
            "JAN": 1,
            "FEB": 2,
            "MAR": 3,
            "APR": 4,
            "MAY": 5,
            "JUN": 6,
            "JUL": 7,
            "AUG": 8,
            "SEP": 9,
            "OCT": 10,
            "NOV": 11,
            "DEC": 12,
        }[month]

        self._dt: _datetime = _datetime(
            int(year),
            month_int,
            int(day),
            int(hour),
            int(minute),
            int(second),
            tzinfo=_timezone.utc,
        )

    @classmethod
    def _from_datetime(cls, dt: _datetime) -> "DateTime":
        """Internal helper to wrap a standard datetime object into a DateTime instance."""
        new_instance = cls.__new__(cls)
        new_instance._dt = dt
        return new_instance

    def __sub__(self, other: _Union["DateTime", _timedelta]) -> _Union["DateTime", _timedelta]:
        if isinstance(other, DateTime):
            return self._dt - other._dt
        if isinstance(other, _timedelta):
            return self._from_datetime(self._dt - other)
        return NotImplemented

    def __add__(self, other: _timedelta) -> "DateTime":
        if isinstance(other, _timedelta):
            return self._from_datetime(self._dt + other)
        return NotImplemented

    def __radd__(self, other: _timedelta) -> "DateTime":
        return self.__add__(other)

    def to_str(self) -> str:
        s = self._dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-7] + 'z'
        return s
