from dataclasses import dataclass, field
from point import Point
from vector import Vector

DEFAULT_LIGHT_POSITION = lambda: Point([0.5, 0.5, 2])
DEFAULT_LIGHT_INTENSITY = 1.0


@dataclass(kw_only=True, slots=True)
class Light:
    position: Point = field(default_factory=DEFAULT_LIGHT_POSITION)
    intensity: int = field(default=DEFAULT_LIGHT_INTENSITY)

    def light_direction(self, point) -> Vector:
        """Computes the light direction from a point
        Args:
            point: The point to which the light direction will be computed from.

        Returns:
            Vector:
        """
        return (self.position - point).normalized
