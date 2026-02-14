from typing import (
    List as _List,
    Final as _Final,
    Optional as _Optional,
    Callable as _Callable,
)
from logging import (
    getLogger as _getLogger,
    basicConfig as _basicConfig,
    WARNING as _WARNING_LOG_LEVEL,
)
from io import (
    StringIO as _StringIO,
)
from csv import (
    DictWriter as _DictWriter,
)
from datetime import (
    datetime as _datetime,
    timedelta as _timedelta,
)
from src.liquid import (
    Liquid as _Liquid,
)
from src.defines.instrument import (
    SymbolLiteral as _SymbolLiteral,
    Session as _Session,
)
from src.defines.candle import (
    Candle as _Candle,
    CandleTypeLiteral as _CandleTypeLiteral,
)

_basicConfig(level=_WARNING_LOG_LEVEL)
_logger = _getLogger(__name__)


class Sequence:
    def __init__(
        self,
        symbol: _SymbolLiteral,
        candle_type: _CandleTypeLiteral,
        candles: _List[_Candle],
    ) -> None:
        self.symbol: _SymbolLiteral = symbol
        self.num_candles: int = len(candles)
        self.candles = candles
        self.candle_type = candle_type
        if len(candles) <= 0 or candle_type == "mo":
            return
        mins: int = {
            "m": 1,
            "5m": 5,
            "15m": 15,
            "30m": 30,
            "h": 60,
            "2h": 120,
            "4h": 240,
            "d": 1440,
            "w": 10080,
        }[candle_type]
        num_gaps = 0
        total_gap_mins = 0.0
        is_seq: _Callable[[_datetime, _datetime], bool] = \
            lambda dt1, dt2: dt1 == (dt2 - _timedelta(minutes=mins))
        prev_: _Candle = candles[0]
        for candle in candles[1:]:
            if not is_seq(prev_.time, candle.time):
                num_gaps += 1
                gap = candle.time - (prev_.time + _timedelta(minutes=mins))
                gapd = gap.days
                gaps = gap.seconds
                total_gap_mins += float((gaps / 60) + 0 if gapd < 1 else (gapd * 1440))
                _logger.warning(f"'{symbol}' candle-times '{prev_.time}' and '{candle.time}' are not sequential")
            prev_ = candle
        self.num_gaps: _Final[int] = num_gaps
        self.avg_gap_mins: _Final[float] = total_gap_mins / num_gaps if num_gaps > 0 else 0.0

    @staticmethod
    def fetch_sequence(
        symbol: _SymbolLiteral,
        candle_type: _CandleTypeLiteral,
        session: _Session,
        client: _Optional[_Liquid] = None,
    ) -> "Sequence":
        liquid_client = client if client else _Liquid.const_with_envvars()
        market_data = liquid_client.get_market_data(
            symbol,
            candle_type,
            session.open_time,
            session.close_time,
        )
        return Sequence(symbol, candle_type, market_data)

    @staticmethod
    def fetch_sequences(
        symbol: _SymbolLiteral,
        candle_type: _CandleTypeLiteral,
        sessions: _List[_Session],
        client: _Optional[_Liquid] = None,
    ) -> _List["Sequence"]:
        liquid_client = client if client else _Liquid.const_with_envvars()
        sequences: _List[Sequence] = []
        for session in sessions:
            sequences.append(
                Sequence.fetch_sequence(
                    symbol,
                    candle_type,
                    session,
                    liquid_client
                )
            )
        return sequences

    def to_csv(self, is_with_header: bool = True) -> str:
        output = _StringIO()
        header = ["timestamp", "open", "high", "low", "close", "volume"]
        writer = _DictWriter(
            output,
            fieldnames=header,
        )

        if is_with_header:
            writer.writeheader()

        for candle in self.candles:
            writer.writerow({
                header[0]: candle.time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                header[1]: candle.open,
                header[2]: candle.high,
                header[3]: candle.low,
                header[4]: candle.close,
                header[5]: candle.volume,
            })
        return output.getvalue()
