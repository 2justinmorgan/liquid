from typing import (
	cast as _cast,
	Optional as _Optional,
	Any as _Any,
	Dict as _Dict,
	Final as _Final,
	List as _List,
	Literal as _Literal,
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


class Liquid:
	def __init__(self, username: str, password: str, api_base_url: str) -> None:
		self._username: _Final[str] = username
		self._password: _Final[str] = password
		self._api_base_url: _Final[str] = api_base_url
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
