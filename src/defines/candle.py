from typing import (
    List as _List,
    Literal as _Literal,
)
from datetime import (
    datetime as _datetime,
)
from pydantic import (
    BaseModel as _BaseModel,
)
from src.defines.instrument import (
    SymbolLiteral as _SymbolLiteral,
)
from src.common import (
    ACCURACY_DECIMALS as _ACCURACY_DECIMALS,
)

CandleTypeLiteral = _Literal["m", "5m", "15m", "30m", "h", "2h", "4h", "d", "w", "mo"]

class _CandleDto(_BaseModel):
    symbol: _SymbolLiteral
    type: _Literal["Candle"]
    candleType: CandleTypeLiteral
    open: float
    close: float
    high: float
    low: float
    volume: float
    time: _datetime

    def to_bo(self) -> "Candle":
        return Candle(self)


class EventsDto(_BaseModel):
    events: _List[_CandleDto]


class Candle:
    def __init__(self, dto: _CandleDto) -> None:
        self.open = dto.open
        self.close = dto.close
        self.high = dto.high
        self.low = dto.low
        self.time = dto.time

        is_increasing = self.open < self.close
        top_middle = self._get_middle(self.high, self.close if is_increasing else self.open)
        bottom_middle = self._get_middle(self.open if is_increasing else self.close, self.low)
        self.middle = self._get_middle(top_middle, bottom_middle)

    def _get_middle(self, num_a: float, num_b: float) -> float:
        return round((num_a + num_b) / 2, _ACCURACY_DECIMALS)

