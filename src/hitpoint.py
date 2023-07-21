from dataclasses import dataclass
from point import Point
from vector import Vector
from geometry import Geometry


@dataclass(kw_only=True, slots=True)
class HitPoint:
    hit: bool = False
    point: Point = None
    distance: float = None
    geometry: Geometry = None

    _normal: Vector = None

    @property
    def normal(self) -> Vector:
        """ Computes the normal of the hitpoint using the geometry's function.

        Returns:
            Vector: The normal of the geometry at the current point.
        """
        if self._normal is None:
            self._normal = self.geometry.normal(self.point)
        return self._normal

    def __lt__(self, other):
        """Compares the distance between the hitpoints and returns True if the distance is less than the other.
        Args:
            other:

        Returns:

        """
        return self.distance < other.distance

    def __ge__(self, other):
        return not self.__lt__(other)
