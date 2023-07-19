from dataclasses import dataclass, field
from point import Point
from vector import Vector

DEFAULT_LIGHT_POSITION = lambda: Point([1, -1, 1])
DEFAULT_LIGHT_INTENSITY = 1.0


@dataclass(kw_only=True, slots=True)
class Light:
    position: Point = field(default_factory=DEFAULT_LIGHT_POSITION)
    intensity: int = field(default=DEFAULT_LIGHT_INTENSITY)
