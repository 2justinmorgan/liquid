from typing import (
    Union as _Union,
    Dict as _Dict,
    Any as _Any,
    Final as _Final,
    cast as _cast,
)
from json import (
    loads as _loads,
)
from os import (
    getenv as _getenv,
    environ as _environ,
)

ACCURACY_DECIMALS: _Final[int] = 8


def get_env(var_name: str) -> str:
    if var_name not in _environ:
        raise KeyError(f"env-var '{var_name}' not found")
    return _cast(str, _getenv(var_name))


def to_dict(json_str: str) -> _Dict[str, _Any]:
    try:
        return _cast(_Dict[str, _Any], _loads(json_str))
    except Exception:
        return {}
