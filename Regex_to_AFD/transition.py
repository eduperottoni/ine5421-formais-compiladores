from dataclasses import dataclass

@dataclass
class Transition:
    source: str
    symbol: str
    target: set[str]

    def __eq__(self, other):
        if isinstance(other, Transition):
            return (
                self.source == other.source and
                self.symbol == other.symbol and
                self.target == other.target
            )
        return False
    
    def __hash__(self):
        return hash((self.source, self.symbol, *self.target))