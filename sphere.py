from volumetric_imports import *
from geometry import Geometry


class Sphere(Geometry):
    __slots__ = "radius"

    def __init__(
        self, *, position=ZERO_POINT, material=None, radius=DEFAULT_RADIUS
    ) -> None:
        """Init a material with provided information.
        If no arguments are provided the object will be at position (0,0,0) with the defautl material

        Args:
            position (Point, optional): Position of the geometry in the scene. Defaults to ZERO_POINT.
        """
        super(Sphere, self).__init__(position=position, material=material)
        self.set_radius(radius)

    def set_radius(self, radius):
        if not isinstance(radius, float):
            raise TypeError(
                "Expected an object of type {0}, but got {1}.".format(
                    float.__name__, radius.__class__.__name__
                )
            )
        self.radius = radius

    def __eq__(self, __value: object) -> bool:
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
