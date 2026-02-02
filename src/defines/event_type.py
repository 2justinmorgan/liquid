from typing import (
    cast as _cast,
    Literal as _Literal,
    Optional as _Optional,
    Dict as _Dict,
)
from src.defines.date_time import DateTime


_Type = _Literal["Candle", "Quote"]
_CandleType = _Literal[
    "m",
    "5m",
    "15m",
    "30m",
    "h",
    "2h",
    "4h",
    "d",
    "w",
    "mo",
]


class EventType:
    def __init__(
        self,
        _type: _Type,
        candle_type: _Optional[_CandleType] = None,
        from_time: _Optional[DateTime] = None,
        to_time: _Optional[DateTime] = None,
    ) -> None:
        self._type: _Type = _type
        self._candle_type: _Optional[_CandleType] = candle_type
        self._from_time: _Optional[DateTime] = from_time
        self._to_time: _Optional[DateTime] = to_time

    def to_dict(self) -> _Dict[str, str]:
        if self._type == "Quote":
            return {
                "type": self._type,
            }
        return {
		    "type": self._type,
		    "candleType": _cast(str, self._candle_type),
		    "fromTime": _cast(DateTime, self._from_time).to_str(),
		    "toTime": _cast(DateTime, self._to_time).to_str(),
		}