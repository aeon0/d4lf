from dataclasses import dataclass


@dataclass
class Aspect:
    type: str | None
    value: float = None
    text: str = ""
    loc: tuple[int, int] = None
