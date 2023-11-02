from dataclasses import dataclass

@dataclass
class State:
    source: set[str]

    def __eq__(self, other):
        if isinstance(other, State):
            return (
                self.source == other.source
            )
        return False
    
    def __hash__(self):
        return hash((self.source, self.symbol, *self.target))