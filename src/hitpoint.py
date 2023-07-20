from dataclasses import dataclass
from point import Point
from vector import Vector
from geometry import Geometry


@dataclass(kw_only=True, slots=True)
class HitPoint:
    hit: bool = False
    point: Point = None
    normal: Vector = None
    distance: float = None
    geometry: Geometry = None

    def __lt__(self, other):
        """Compares the distance between the hitpoints and returns True if the distance is less than the other.
        Args:
            other:

        Returns:

        """
        return self.distance < other.distance

    def __ge__(self, other):
        return not self.__lt__(other)
