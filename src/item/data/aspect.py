from dataclasses import dataclass


@dataclass
class Aspect:
    type: str
    text: str
    value: float = None
