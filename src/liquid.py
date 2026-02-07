from typing import (
	cast as _cast,
	Optional as _Optional,
	Any as _Any,
	Dict as _Dict,
	Final as _Final,
	List as _List,
	Literal as _Literal,
)
from random import (
	choices as _choices,
)
from string import (
	digits as _digits,
	ascii_letters as _ascii_letters,
)
from urllib.parse import (
	quote as _quote,
)
from requests import (
    request as _request,
	Response as _Response,
)
from datetime import (
	datetime as _datetime,
	timedelta as _timedelta,
)
from http import HTTPMethod as _HTTPMethod
from src.common import (
	to_dict as _to_dict,
)
from src.defines.instrument import (
	InstrumentsDtoCollection as _InstrumentsDtoCollection,
	Instrument as _Instrument,
	SymbolLiteral as _SymbolLiteral,
)
from src.defines.candle import (
	Candle as _Candle,
	CandleTypeLiteral as _CandleTypeLiteral,
	EventsDto as _EventsDto,
)
from src.defines.position import (
	Position as _Position,
	PositionsDto as _PositionsDto,
	TradeSideLiteral as _TradeSideLiteral,
)


class Liquid:
	def __init__(
		self,
		username: str,
		password: str,
		api_base_url: str,
		account_id: str,
	) -> None:
		self._username: _Final[str] = username
		self._password: _Final[str] = password
		self._api_base_url: _Final[str] = api_base_url
		self._account_code: _Final[str] = _quote(f"default:{account_id}")
		self._session_token: str = self._get_session_token(
			self._username,
			self._password,
		)

	def _get_session_token(self, username: str, password: str) -> str:
		tkey = "sessionToken"
		result = self._query(
			_HTTPMethod.POST,
			"/login",
			{
				"username": username,
				"password": password,
				"domain": "default",
			},
		).json()
		if not isinstance(result, dict) or not isinstance(result.get(tkey), str):
			raise TypeError(f"session token not received", result)
		return _cast(str, result.get(tkey))

	def _query(
		self,
		method: _HTTPMethod,
		api_url_path: str,
		data: _Optional[_Dict[str, _Any]] = None,
		num_retries: _Optional[int] = None,
	) -> _Response:
		if (num_retries or 0) > 2:
			raise Exception("too many retries")

		base_url = self._api_base_url
		url = f"{base_url}/dxsca-web{'/' if api_url_path[0] != '/' else ''}{api_url_path}"
		response = _request(
	        method=method,
			headers={
				"Content-Type": "application/json",
				**({"Authorization": f"DXAPI {self._session_token}"} if getattr(self, "_session_token", None) else {})
			},
	        json=data,
			url=url,
		)
		if _to_dict(response.text).get("description") == "Authorization required":
			self._session_token = \
				self._get_session_token(self._username, self._password)
			return self._query(method, api_url_path, data, (num_retries or 0) + 1)
		return response

	def get_instruments(self) -> _List[_Instrument]:
		result = self._query(
			_HTTPMethod.GET,
			"instruments/query",
		).json()
		if not isinstance(result, dict) or "instruments" not in result:
			raise TypeError(f"instruments not received", result)
		dtos = _InstrumentsDtoCollection(**result)
		return [dto.to_bo() for dto in dtos.instruments]

	def get_market_data(
		self,
		symbol: _SymbolLiteral,
		duration: _CandleTypeLiteral,
		from_time: _datetime,
		to_time: _datetime,
	) -> _List[_Candle]:
		if from_time >= to_time:
			raise ValueError("'from_time' must be a date-time before 'to_time'")
		response = self._query(
			_HTTPMethod.POST,
			"marketdata",
			{
				"symbols": [symbol],
				"eventTypes": [
					{
						"type": "Candle",
						"candleType": duration,
						"fromTime": from_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-7] + 'z',
						"toTime": to_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-7] + 'z',
					},
				],
			},
		).json()
		if not isinstance(response, dict) or "events" not in response:
			raise TypeError(f"market data not received", response)
		dtos = _EventsDto(**response)
		return [dto.to_bo() for dto in dtos.events]

	def get_open_positions(self) -> _List[_Position]:
		response = self._query(
			_HTTPMethod.GET,
			f"accounts/{self._account_code}/positions",
		).json()
		if not isinstance(response, dict) or "positions" not in response:
			raise TypeError(f"positions not received", response)
		dtos = _PositionsDto(**response).positions
		return [dto.to_bo() for dto in dtos]

	def place_order(
		self,
		symbol: _SymbolLiteral,
		order_type: _Literal["MARKET", "LIMIT", "STOP"],
		side: _TradeSideLiteral,
		effect: _Literal["OPEN", "CLOSE"],
		quantity: float,
		position_code: _Optional[str] = None,
		limit_price: _Optional[float] = None,
		stop_price: _Optional[float] = None,
	) -> str:
		order_code = ''.join(_choices(_ascii_letters + _digits, k=7))
		response = self._query(
			_HTTPMethod.POST,
			f"accounts/{self._account_code}/orders",
			{
				"orderCode": order_code,
				"type": order_type,
				"instrument": symbol,
				"quantity": quantity,
				"side": side,
				"positionEffect": effect,
				"tif": "GTC",
				**({"positionCode": position_code} if position_code is not None else {}),
				**({"limitPrice": limit_price} if limit_price is not None else {}),
				**({"stopPrice": stop_price} if stop_price is not None else {}),
			},
		).json()
		if not isinstance(response, dict) or not "orderId" in response:
			raise TypeError("order not successful", response)
		return _cast(str, response["orderId"])
