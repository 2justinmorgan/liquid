from typing import (
    List as _List,
    Optional as _Optional,
    Literal as _Literal,
)
from datetime import (
    datetime as _datetime,
)
from pydantic import (
    BaseModel as _BaseModel,
    Field as _Field,
    field_validator as _field_validator,
)
from src.defines.position import (
    TradeSideLiteral as _TradeSideLiteral,
)
from src.defines.instrument import (
    SymbolLiteral as _SymbolLiteral,
    CurrencyLiteral as _CurrencyLiteral,
)

PositionEffectLiteral = _Literal["OPEN", "CLOSE"]
OrderTypeLiteral = _Literal["MARKET", "LIMIT", "STOP"]
TifLiteral = _Literal["GTC", "DAY", "GTD"]
_OrderStatusLiteral = _Literal[
    "ACCEPTED",
    "WORKING",
    "CANCELED",
    "COMPLETED",
    "EXPIRED",
    "REJECTED",
]
_CashTransactionTypeLiteral = _Literal[
    "COMMISSION",
    "FINANCING",
    "DEPOSIT",
    "WITHDRAWAL",
    "SETTLEMENT",
    "COST",
    "EX_DIVIDEND",
    "REBATE",
    "NEGATIVE_BALANCE_CORRECTION",
    "BUST",
]


class _OrderLegDto(_BaseModel):
    instrument: _SymbolLiteral
    position_effect: PositionEffectLiteral = _Field(alias="positionEffect")
    position_code: str = _Field(alias="positionCode")
    leg_ratio: float = _Field(alias="legRatio")
    quantity: float
    filled_quantity: float = _Field(alias="filledQuantity")
    remaining_quantity: float = _Field(alias="remainingQuantity")
    average_price: float = _Field(alias="averagePrice")


class _ExecutionDto(_BaseModel):
    account: str
    execution_code: str = _Field(alias="executionCode")
    order_code: str = _Field(alias="orderCode")
    update_order_id: int = _Field(alias="updateOrderId")
    version: int
    client_order_id: _Optional[str] = _Field(None, alias="clientOrderId")
    action_code: str = _Field(alias="actionCode")
    instrument: _Optional[_SymbolLiteral] = _Field(None)
    status: _OrderStatusLiteral
    final_status: bool = _Field(alias="finalStatus")
    filled_quantity: float = _Field(alias="filledQuantity")
    last_quantity: float = _Field(alias="lastQuantity")
    filled_quantity_notional: float = _Field(alias="filledQuantityNotional")
    last_quantity_notional: float = _Field(alias="lastQuantityNotional")
    remaining_quantity: _Optional[float] = _Field(None, alias="remainingQuantity")
    last_price: _Optional[float] = _Field(None, alias="lastPrice")
    average_price: _Optional[float] = _Field(None, alias="averagePrice")
    transaction_time: _datetime = _Field(alias="transactionTime")


class _CashTransactionDto(_BaseModel):
    account: str
    transaction_code: str = _Field(alias="transactionCode")
    order_code: str = _Field(alias="orderCode")
    trade_code: str = _Field(alias="tradeCode")
    version: int
    client_order_id: _Optional[str] = _Field(None, alias="clientOrderId")
    transaction_type: _CashTransactionTypeLiteral = _Field(alias="type")
    value: float
    currency: _CurrencyLiteral
    transaction_time: _datetime = _Field(alias="transactionTime")

    @_field_validator('currency', mode='before')
    @classmethod
    def clean_currency(cls, v: str) -> str:
        if isinstance(v, str):
            return v.replace('$', '').strip()
        return v


class HistoricalOrderDto(_BaseModel):
    account: str
    version: int
    order_id: int = _Field(alias="orderId")
    order_code: str = _Field(alias="orderCode")
    client_order_id: _Optional[str] = _Field(None, alias="clientOrderId")
    action_code: str = _Field(alias="actionCode")
    leg_count: int = _Field(alias="legCount")
    order_type: OrderTypeLiteral = _Field(alias="type")
    instrument: _SymbolLiteral
    status: _OrderStatusLiteral
    final_status: bool = _Field(alias="finalStatus")
    legs: _List[_OrderLegDto]
    side: _TradeSideLiteral
    tif: TifLiteral
    issue_time: _datetime = _Field(alias="issueTime")
    transaction_time: _datetime = _Field(alias="transactionTime")
    executions: _List[_ExecutionDto]
    cash_transactions: _List[_CashTransactionDto] = _Field(alias="cashTransactions")
