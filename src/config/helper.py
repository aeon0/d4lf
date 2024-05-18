"""New config loading and verification using pydantic. For now, both will exist in parallel hence _new."""

import keyboard._winkeyboard

# propagate the key names to the keyboard module
keyboard._winkeyboard._setup_name_tables()


def check_greater_than_zero(v: int) -> int:
    if v < 0:
        raise ValueError("must be greater than zero")
    return v


def key_must_exist(k: str) -> str:
    if k not in keyboard._winkeyboard.from_name:
        raise ValueError("key does not exist")
    return k


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def str_to_int_list(s: str) -> list[int]:
    if not s:
        return []
    return [int(x) for x in s.split(",")]
