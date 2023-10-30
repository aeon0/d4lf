from dataclasses import dataclass


@dataclass
class Affix:
    type: str
    text: str
    value: float = None
