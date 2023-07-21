from camera import Camera
from dataclasses import dataclass, field
from geometry import Geometry
from light import Light
from point_light import PointLight
from sphere import Sphere


@dataclass(kw_only=True, slots=True)
class Scene:
    camera: Camera = field(default_factory=lambda: Camera())
    geometries: list[Geometry] = field(default_factory=lambda: [Sphere()])
    light: Light = field(default_factory=lambda: PointLight())
