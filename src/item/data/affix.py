from dataclasses import dataclass


@dataclass
class Affix:
    type: str
    value: float = None
    text: str = ""
