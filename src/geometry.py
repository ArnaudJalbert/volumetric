from dataclasses import dataclass, field
from point import Point
from vector import Vector

DEFAULT_GEOMETRY_POSITION = lambda: Point([0, 0, 0])
DEFAULT_GEOMETRY_COLOR = lambda: (1, 1, 1)
X_NORMAL_OFFSET = Point([0.001, 0, 0])
Y_NORMAL_OFFSET = Point([0, 0.001, 0])
Z_NORMAL_OFFSET = Point([0, 0, 0.001])


@dataclass(kw_only=True, slots=True)
class Geometry(object):
    position: Point = field(default_factory=DEFAULT_GEOMETRY_POSITION)
    color: tuple[int] = field(default_factory=DEFAULT_GEOMETRY_COLOR)
    visible: bool = True

    def __eq__(self, __value: object) -> bool:
        """Equal if the positions are equal.

        Args:
            __value (object): Geometry object to compare with.

        Returns:
            bool: True if the positions are equal.
        """
        return (
            issubclass(__value.__class__, Geometry)
            and __value.position == self.position
        )

    def map(self, point: Point) -> float:
        """Estimates the distance between the point and the geometry.
        This function defines the geometry. It needs to be a 3D function that returns the distance from the point.
        It needs to be overriden by the concrete class.

        Args:
            point (Point): Current point on in 3D space.

        Returns:
            float: The approximate distance between the point and the geometry.
        """
        pass

    def normal(self, point: Point) -> Vector:
        """Computes the normal of a point in the geometry from a hitpoint.

        Args:
            point: The point from which to compute the normal from.

        Returns:
            Vector: The normalized vector of the computed normal.
        """
        x_normal = self.map(point + X_NORMAL_OFFSET) - self.map(point - X_NORMAL_OFFSET)
        y_normal = self.map(point + Y_NORMAL_OFFSET) - self.map(point - Y_NORMAL_OFFSET)
        z_normal = self.map(point + Z_NORMAL_OFFSET) - self.map(point - Z_NORMAL_OFFSET)
        normal = Vector([x_normal, y_normal, z_normal])
        normal.normalize()
        return normal
