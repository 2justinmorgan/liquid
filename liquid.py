from typing import (
    Optional as _Optional,
	List as _List,
)
from requests import request as _request
from http import HTTPMethod as _HTTPMethod
from common import get_env as _get_env


def _query(
	method: _HTTPMethod,
	api_url_path: str,
	data: _Optional[dict] = None,
	session_token: _Optional[str] = None,
) -> dict:
	base_url = _get_env("LIQUID_API_BASE_URL")
	url = f"{base_url}{'/' if api_url_path[0] != '/' else ''}{api_url_path}"
	return _request(
        method=method,
		headers={
			"Content-Type": "application/json",
			**({"Authorization": f"DXAPI {session_token}"} if session_token else {})
		},
        json=data,
		url=url,
	).json()


def _get_session_token() -> str:
	return _query(
		_HTTPMethod.POST,
		"/dxsca-web/login",
		{
			"username": _get_env("LIQUID_UN"),
			"password": _get_env("LIQUID_PW"),
			"domain": "default",
		},
	).get("sessionToken")


def get_instruments() -> _List:
	return _query(
		_HTTPMethod.GET,
		"dxsca-web/instruments/query",
		None,
		_get_session_token(),
	)
