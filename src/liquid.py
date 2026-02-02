from typing import (
	cast as _cast,
	Optional as _Optional,
	Any as _Any,
	Dict as _Dict,
	List as _List,
)
from requests import (
    request as _request,
	Response as _Response,
)
from http import HTTPMethod as _HTTPMethod
from random import choices as _choices
from string import (
	digits as _digits,
	ascii_letters as _ascii_letters,
)
from src.common import get_env as _get_env
from src.enums.symbols import Symbol
from src.defines.event_type import EventType
TOK = None


def _query(
	method: _HTTPMethod,
	api_url_path: str,
	data: _Optional[_Dict[str, _Any]] = None,
	session_token: _Optional[str] = None,
) -> _Response:
	base_url = _get_env("LIQUID_API_BASE_URL")
	url = f"{base_url}/dxsca-web{'/' if api_url_path[0] != '/' else ''}{api_url_path}"
	return _request(
        method=method,
		headers={
			"Content-Type": "application/json",
			**({"Authorization": f"DXAPI {session_token}"} if session_token else {})
		},
        json=data,
		url=url,
	)


def _get_session_token() -> str:
	tkey = "sessionToken"
	result = _query(
		_HTTPMethod.POST,
		"/login",
		{
			"username": _get_env("LIQUID_UN"),
			"password": _get_env("LIQUID_PW"),
			"domain": "default",
		},
	).json()
	if not isinstance(result, dict) or not isinstance(result.get(tkey), str):
		raise TypeError(f"session token not received")
	return _cast(str, result.get(tkey))


def get_instruments() -> _Dict[str, _Any]:
	result = _query(
		_HTTPMethod.GET,
		"instruments/query",
		None,
		TOK,
	)
	return result.json()
	if not isinstance(result, dict):
		raise TypeError(f"instruments not received")
	return result


def get_market_data(
	symbols: _List[Symbol],
	event_types: _List[EventType],
):
	d = 		{
		  "symbols": [symbol for symbol in symbols],
		  "eventTypes": [event_type.to_dict() for event_type in event_types],
		}
	print(d)
	return _query(
		_HTTPMethod.POST,
		"marketdata",
		d,
		TOK,
	).json()


def _to_account_id(username: str) -> str:
	return f"default%3A{username}"


def place_order(username: str, symbol: Symbol):
	order_code = ''.join(_choices(_ascii_letters + _digits, k=7))
	return _query(
		_HTTPMethod.POST,
		f"accounts/{_to_account_id(username)}/orders",
		{
			"orderCode": order_code,
			"type": "MARKET",
			"instrument": symbol,
			"quantity": 10,
			"side": "BUY",
			"positionEffect": "OPEN",
			"tif": "GTC",
		},
		TOK,
	)


def get_user_details(username: str):
	return _query(
		_HTTPMethod.GET,
		f"users/{username}",
		None,
		TOK,
	)


def get_portfolio(username: str):
	return _query(
		_HTTPMethod.GET,
		f"accounts/{_to_account_id(username)}/orders",
		None,
		TOK,
	)


def get_open_positions(username: str):
	return _query(
		_HTTPMethod.GET,
		f"accounts/{_to_account_id(username)}/positions",
		None,
		TOK,
	)


def get_order_history(username: str):
	return _query(
		_HTTPMethod.GET,
		f"accounts/{_to_account_id(username)}/orders/history",
		None,
		TOK,
	)

TOK = _get_session_token()