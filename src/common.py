from os import (
    getenv as _getenv,
    environ as _environ,
)


def get_env(var_name: str) -> str:
    if var_name not in _environ:
        raise KeyError(f"env-var '{var_name}' not found")
    return _getenv(var_name)
