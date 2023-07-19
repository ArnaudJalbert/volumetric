from dataclasses import dataclass
from point import Point
from vector import Vector


@dataclass(kw_only=True, slots=True)
class HitPoint:
    hit: bool = False
    point: Point = None
    normal: Vector = None
    distance: float = None
