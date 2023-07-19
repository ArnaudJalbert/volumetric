from dataclasses import dataclass, field
from point import Point

DEFAULT_GEOMETRY_POSITION = lambda: Point([0, 0, 0])
DEFAULT_GEOMETRY_COLOR = lambda: (255, 255, 255)


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

    def map(self, point: Point):
        """Estimates the distance between the point and the geometry.
        This function defines the geometry. It needs to be a 3D function that returns the distance from the point.
        It needs to be overriden by the concrete class.

        Args:
            point (Point): Current point on in 3D space.

        Returns:
            float: The approximate distance between the point and the geometry.
        """
        pass
