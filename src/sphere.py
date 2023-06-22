from volumetric_imports import *
from geometry import Geometry
from dataclasses import dataclass, field


@dataclass
class Sphere(Geometry):
    radius: float = DEFAULT_RADIUS

    def __eq__(self, __value: object) -> bool:
        """Equal if the base geometry attributes are equal and the radiuses

        Args:
            __value (object): Sphere object to compare with.

        Returns:
            bool: If the base geometry are and the radiuses are equal.
        """
        return super().__eq__(__value) and __value.radius == self.radius

    def map(self, point: Point):
        """Estimates the distance between the point and the geometry.
        Algorithm: https://iquilezles.org/articles/distfunctions/

        Args:
            point (Point): Current point on in 3D space.

        Returns:
            float: The approximate distance between the point and the geometry.
                   The value is 0 if the point is inside the geometry.
        """
        return distance if (distance := point.length - self.radius) >= 0 else 0
