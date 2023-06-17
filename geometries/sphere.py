from geometry.geometry import Geometry
from pyrr import Vector3, Vector4


class Sphere(Geometry):

    def __init__(self, color=Vector4([1., 1., 1., 1.]), center=Vector3(1, 1, 1), radius=1):
        super().__init__(color=color)
        self.center = center
        self.radius = radius

    def map(self, p: Vector3) -> float:
        length = p.length()
        distance = length - self.radius
        return distance

