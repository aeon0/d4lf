from functools import wraps
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable

    from src.type_aliases import JsonValue


def convert_args_to_numpy[R](func: Callable[..., R]) -> Callable[..., R]:
    @wraps(func)
    def wrapper(*args: JsonValue | np.ndarray, **kwargs: JsonValue | np.ndarray) -> R:
        converted_args = [np.array(arg) if isinstance(arg, list | tuple) else arg for arg in args]
        converted_kwargs = {
            key: np.array(value) if isinstance(value, list | tuple) else value for key, value in kwargs.items()
        }
        return func(*converted_args, **converted_kwargs)

    return wrapper
