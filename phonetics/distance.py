from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Distance:
    actual: float
    total: float = 1.0
    
    def normalized(self) -> float:
        return self.actual / self.total
    
    def __add__(self, other: Distance) -> Distance:
        return Distance(self.actual + other.actual, self.total + other.total)
    
    def __mul__(self, factor: float) -> Distance:
        return Distance(self.actual * factor, self.total * factor)
    __rmul__ = __mul__
    
    def __truediv__(self, divider: float) -> Distance:
        return Distance(self.actual / divider, self.total / divider)
    
    @classmethod
    def empty(cls) -> Distance:
        return Distance(0.0, 0.0)
