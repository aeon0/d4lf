from dataclasses import dataclass


@dataclass
class Aspect:
    type: str
    value: float = None
    text: str = ""
    loc: tuple[int, int] = None

    def __eq__(self, other: "Aspect") -> bool:
        if not isinstance(other, Aspect):
            return False
        return self.type == other.type and self.value == other.value
