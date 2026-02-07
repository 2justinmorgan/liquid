from typing import (
    Literal as _Literal,
    List as _List,
    Final as _Final,
)
from pydantic import (
    BaseModel as _BaseModel,
    Field as _Field,
)
from datetime import (
    datetime as _datetime,
)
from src.defines.instrument import (
    SymbolLiteral as _SymbolLiteral,
)

TradeSideLiteral = _Literal["BUY", "SELL"]


class _PositionDto(_BaseModel):
    account: str
    version: int
    position_code: str = _Field(alias="positionCode")
    symbol: _SymbolLiteral
    quantity: float
    side: TradeSideLiteral
    quantity_notional: float = _Field(alias="quantityNotional")
    open_time: _datetime = _Field(alias="openTime")
    open_price: float = _Field(alias="openPrice")
    last_update_time: _datetime = _Field(alias="lastUpdateTime")
    margin_rate: float = _Field(alias="marginRate")

    def to_bo(self) -> "Position":
        return Position(self)


class PositionsDto(_BaseModel):
    positions: _List[_PositionDto]


class Position:
    def __init__(self, dto: _PositionDto) -> None:
        self.account: _Final[str] = dto.account
        self.version: _Final[int] = dto.version
        self.position_code: _Final[str] = dto.position_code
        self.symbol: _Final[_SymbolLiteral] = dto.symbol
        self.quantity: _Final[float] = dto.quantity
        self.side: _Final[TradeSideLiteral] = dto.side
        self.quantity_notional: _Final[float] = dto.quantity_notional
        self.open_time: _Final[_datetime] = dto.open_time
        self.open_price: _Final[float] = dto.open_price
        self.last_update_time: _Final[_datetime] = dto.last_update_time
        self.margin_rate: _Final[float] = dto.margin_rate
