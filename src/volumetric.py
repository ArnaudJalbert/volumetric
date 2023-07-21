from colour import Color
from geometry import Geometry
from hitpoint import HitPoint
from itertools import product as cartesian_product, repeat
from scene import Scene
from vector import Vector

DEFAULT_MAX_RAYMARCH_STEPS = 1000
DEFAULT_MAX_DISTANCE = 100
DEFAULT_EPSILON = 0.001


class volumetric:
    scene = None
    pixel_buffer = None
    max_raymarch_steps = DEFAULT_MAX_RAYMARCH_STEPS
    max_distance = DEFAULT_MAX_DISTANCE
    epsilon = DEFAULT_EPSILON

    def __init__(self, scene: Scene) -> None:
        self.scene = scene
        self.pixel_buffer = self._pixel_buffer_factory(
            self.scene.camera.height * self.scene.camera.width
        )

    @staticmethod
    def _pixel_buffer_factory(size):
        return [None] * size

    def _raymarch(self, geometry: Geometry, ray: Vector) -> HitPoint:
        """_summary_

        Args:
            geometry (Geometry): _description_
            ray (Vector): _description_

        Returns:
            tuple: _description_
        """
        total_distance = 0
        distance = 0

        for _ in repeat(None, self.max_raymarch_steps):
            if distance > self.max_distance:
                return HitPoint()

            point = self.scene.camera.position + ray * total_distance
            distance = geometry.map(point)

            if distance < self.epsilon:
                return HitPoint(
                    hit=True, point=point, distance=total_distance, geometry=geometry
                )

            total_distance += distance

        return HitPoint()

    def _compute_shading(self, hitpoint: HitPoint) -> tuple:
        attenuation = float(
            self.scene.light.light_direction(hitpoint.point).dot(hitpoint.normal)
            * self.scene.light.intensity
        )
        return tuple(
            int(color * attenuation * 255) for color in hitpoint.geometry.color
        )

    @staticmethod
    def _compute_background_color() -> tuple:
        return 50, 50, 50

    def _compute_pixel_color(self, position_y: int, position_x: int) -> tuple:
        """Computes the pixel color at position [position_x, position_y] of the image
        plane of the current scene.

        If there is an
        Args:
            position_x (int): Position x of the pixel
            position_y (int): Position y of the pixel

        Returns:
            Color: The computed color of the pixel
        """
        camera_ray = self.scene.camera.generate_ray_direction(position_x, position_y)
        hitpoints = []

        for geometry in self.scene.geometries:
            hitpoint = self._raymarch(geometry, camera_ray)
            if hitpoint.hit:
                hitpoints.append(self._raymarch(geometry, camera_ray))

        if hitpoints:
            closest_hitpoint = min(hitpoints)
            return self._compute_shading(closest_hitpoint)

        return self._compute_background_color()

    def execute(self) -> list:
        """Iterates over each pixel.
        Computes the color of each pixel.
        Stores the pixel color in the buffer

        Returns:
            list[tuple]: The buffer of the colors of each pixel.
        """
        width = self.scene.camera.width
        height = self.scene.camera.height
        pixel_positions = cartesian_product(range(width), range(height))
        self.scene.camera.init_camera_geometry()

        for position_y, position_x in pixel_positions:
            self.pixel_buffer[
                position_x * width + position_y
            ] = self._compute_pixel_color(position_y, position_x)

        return self.pixel_buffer
