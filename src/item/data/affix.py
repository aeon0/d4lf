from dataclasses import dataclass


@dataclass
class Affix:
    type: str
    value: float = None
    text: str = ""
    loc: tuple[int, int] = None

    def __eq__(self, other: "Affix") -> bool:
        if not isinstance(other, Affix):
            return False
        return self.type == other.type and self.value == other.value
