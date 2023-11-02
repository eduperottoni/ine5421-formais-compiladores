from dataclasses import dataclass

@dataclass
class State:
    source: list[int]

    def __eq__(self, other):
        if isinstance(other, State):
            return (
                set(self.source) == set(other.source)
            )
        return False
    
    def __hash__(self):
        return hash((self.source, self.symbol, *self.target))